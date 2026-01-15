import os
import time
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from models.request_models import QueryRequest, RegisterRequest, LoginRequest
from models.response_models import QueryResponse, SchemaResponse
from services.query_service import handle_query
from services.schema_service import get_schema_response, refresh_schema_cache
from services.user_service import create_user, authenticate_user, get_user_by_email
from services.auth_service import require_user, optional_user
from services.history_service import HistoryService
from services.db_service import get_session, init_db
from schemas.history import HistoryListResponse, HistoryCreate
from config.logging_config import logger

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app: FastAPI = FastAPI()

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Enable CORS
# Note: When allow_credentials=True, allow_origins cannot be ["*"]
# Must specify exact origins for browser credential requests

allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
]

# Add production frontend URL if set
FRONTEND_URL = os.getenv("FRONTEND_URL", "")
if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)
    logger.info(f"Added production frontend URL to CORS: {FRONTEND_URL}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint for monitoring and load balancers.
    Returns detailed status of database and OpenAI API configuration.
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Check database connection
    try:
        db = get_session()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Health check - database unhealthy: {e}")
    
    # Check OpenAI API key configuration
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        health_status["checks"]["openai_api"] = "configured"
    else:
        health_status["checks"]["openai_api"] = "not_configured"
        health_status["status"] = "degraded"
    
    # Return dict directly - FastAPI automatically converts to JSON
    return health_status

@app.get("/me")
def get_me(user_id: str = Depends(optional_user)):  # Returns user_id
    if not user_id:
        return {"email": None, "full_name": None}
    from services.user_service import get_user_by_id
    user = get_user_by_id(user_id)
    if not user:
        return {"email": None, "full_name": None}
    return {
        "email": user["email"],
        "full_name": user["full_name"]
    }

@app.post("/register")
def register_user(request: RegisterRequest):
    success = create_user(request.full_name, request.email, request.password)
    if not success:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "User registered successfully"}

@app.post("/login")
def login_user(response: Response, request: LoginRequest):
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Store user_id in cookie for efficient lookups
    response.set_cookie(key="user_id", value=user["id"], httponly=True)
    return {"message": "Login successful", "full_name": user["full_name"]}

@app.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("user_id")
    return {"message": "Logged out successfully"}

@app.get("/protected")
def protected_route(user_id: str = Depends(require_user)):  # Returns user_id
    return {"message": f"Welcome, you are logged in!"}

@app.post("/query", response_model=QueryResponse)
@limiter.limit("20/minute")  # 20 queries per minute per IP
async def process_query(
    request: Request,
    payload: QueryRequest,
    user_id: str = Depends(optional_user)  # Returns user_id if authenticated
) -> QueryResponse:
    """
    Process natural language query and return SQL results.
    
    Rate limited to 20 queries per minute per IP address to prevent abuse.
    Input validation ensures query quality and prevents misuse.
    """
    start_time = time.time()
    question = payload.question
    
    # Input validation
    if not question or not question.strip():
        logger.warning(f"Empty query attempted from IP: {get_remote_address(request)}")
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    if len(question) > 500:
        logger.warning(f"Query too long ({len(question)} chars) from IP: {get_remote_address(request)}")
        raise HTTPException(
            status_code=400,
            detail="Question too long (maximum 500 characters)"
        )
    
    # Reject queries with suspicious patterns (basic protection)
    suspicious_patterns = ["DROP TABLE", "DELETE FROM", "TRUNCATE", "ALTER TABLE", "DROP DATABASE"]
    question_upper = question.upper()
    for pattern in suspicious_patterns:
        if pattern in question_upper:
            logger.warning(f"Suspicious query pattern detected: {pattern} from IP: {get_remote_address(request)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid query pattern detected"
            )
    
    try:
        # Process query
        result = handle_query(question)
        
        # Log successful query metrics
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Query processed successfully",
            extra={
                "extra_data": {
                    "duration_ms": duration_ms,
                    "user_id": user_id if user_id else "anonymous",
                    "question_length": len(question),
                    "result_rows": len(result.raw_rows) if result.raw_rows else 0,
                }
            }
        )
        
        # Save to history if user is authenticated
        if user_id:
            db = get_session()
            try:
                history_data = HistoryCreate(
                    question=question,
                    sql_query=result.sql_query,
                    status=result.status,
                    execution_time=result.execution_time,
                    results=result.results,
                    raw_rows=result.raw_rows,
                    error_message=result.error_message
                )
                HistoryService.create_history_entry(db, user_id, history_data)
            except Exception as e:
                # Don't fail the query if history save fails
                logger.error(f"Failed to save history: {e}")
            finally:
                db.close()
        
        return result
        
    except Exception as e:
        # Log failed query
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"Query processing failed: {str(e)}",
            extra={
                "extra_data": {
                    "duration_ms": duration_ms,
                    "user_id": user_id if user_id else "anonymous",
                    "error": str(e),
                }
            }
        )
        raise

@app.get("/schema", response_model=SchemaResponse)
async def get_schema() -> SchemaResponse:
    return get_schema_response()

@app.get("/refresh-schema", response_model=SchemaResponse)
async def refresh_schema() -> SchemaResponse:
    return refresh_schema_cache()

@app.get("/history", response_model=HistoryListResponse)
def get_history(
    user_id: str = Depends(require_user),
    page: int = 1,
    per_page: int = 20
):
    """Get paginated query history for authenticated user."""
    db = get_session()
    try:
        return HistoryService.get_user_history(db, user_id, page, per_page)
    finally:
        db.close()

@app.delete("/history")
def clear_history(user_id: str = Depends(require_user)):
    """Clear all query history for authenticated user."""
    db = get_session()
    try:
        deleted_count = HistoryService.clear_user_history(db, user_id)
        return {"message": f"Deleted {deleted_count} history entries"}
    finally:
        db.close()
