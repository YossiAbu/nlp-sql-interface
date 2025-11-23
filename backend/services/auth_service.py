# services/auth_service.py
from typing import Optional
from fastapi import Request, HTTPException, status

def require_user(request: Request) -> str:
    """Returns user_id if authenticated, raises 401 otherwise."""
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user_id

def optional_user(request: Request) -> Optional[str]:
    """Returns user_id if authenticated, None otherwise. Never raises."""
    return request.cookies.get("user_id")
