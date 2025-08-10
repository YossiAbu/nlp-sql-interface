from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from models.request_models import QueryRequest, RegisterRequest, LoginRequest
from models.response_models import QueryResponse, SchemaResponse
from services.query_service import handle_query
from services.schema_service import get_schema_response, refresh_schema_cache
from services.user_service import create_user, authenticate_user, get_user_by_email
from services.auth_service import require_user, optional_user  # ✅ updated import

app: FastAPI = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/me")
def get_me(user_email: str = Depends(optional_user)):  # ✅ use optional_user
    if not user_email:
        return {"email": None, "full_name": None}
    user = get_user_by_email(user_email)
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
    response.set_cookie(key="user_email", value=user["email"], httponly=True)
    return {"message": "Login successful", "full_name": user["full_name"]}

@app.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("user_email")
    return {"message": "Logged out successfully"}

@app.get("/protected")
def protected_route(user_email: str = Depends(require_user)):  # ✅ use require_user
    return {"message": f"Welcome {user_email}, you are logged in!"}

@app.post("/query", response_model=QueryResponse)
async def process_query(
    payload: QueryRequest,
    user_email: str = Depends(optional_user)  # ✅ allow anonymous queries
) -> QueryResponse:
    return handle_query(payload.question)

@app.get("/schema", response_model=SchemaResponse)
async def get_schema() -> SchemaResponse:
    return get_schema_response()

@app.get("/refresh-schema", response_model=SchemaResponse)
async def refresh_schema() -> SchemaResponse:
    return refresh_schema_cache()
