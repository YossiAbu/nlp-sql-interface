# models/request_models.py
from pydantic import BaseModel, EmailStr

class QueryRequest(BaseModel):
    question: str

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
