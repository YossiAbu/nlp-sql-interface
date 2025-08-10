# services/auth_service.py
from typing import Optional
from fastapi import Request, HTTPException, status

def require_user(request: Request) -> str:
    email = request.cookies.get("user_email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return email

def optional_user(request: Request) -> Optional[str]:
    # Returns None if unauthenticated; never raises
    return request.cookies.get("user_email")
