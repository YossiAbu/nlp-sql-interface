from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from models.request_models import QueryRequest, RegisterRequest, LoginRequest
from models.response_models import QueryResponse, SchemaResponse
from services.query_service import handle_query
from services.schema_service import get_schema_response, refresh_schema_cache
from services.user_service import create_user, authenticate_user, get_user_by_email
from services.auth_service import require_user, optional_user
from services.history_service import HistoryService
from services.db_service import get_session, init_db
from schemas.history import HistoryListResponse, HistoryCreate

app: FastAPI = FastAPI()

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Enable CORS
# Note: When allow_credentials=True, allow_origins cannot be ["*"]
# Must specify exact origins for browser credential requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite dev server (alternate port)
        "http://localhost:3000",  # Alternative dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Simple health check endpoint for deployment and testing"""
    return {"status": "ok"}

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
async def process_query(
    payload: QueryRequest,
    user_id: str = Depends(optional_user)  # Returns user_id if authenticated
) -> QueryResponse:
    result = handle_query(payload.question)
    
    # Save to history if user is authenticated
    if user_id:
        db = get_session()
        try:
            history_data = HistoryCreate(
                question=payload.question,
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
            print(f"Failed to save history: {e}")
        finally:
            db.close()
    
    return result

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
