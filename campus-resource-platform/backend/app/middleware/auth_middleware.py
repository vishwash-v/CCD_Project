"""
Auth middleware — extracts and validates JWT tokens from requests.
Provides dependency injection for protected routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import decode_access_token
from app.services.cloudant_service import db, DB_USERS

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    FastAPI dependency that extracts the current user from the JWT token.
    Raises 401 if token is invalid or user not found.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await db.get_document(DB_USERS, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency that requires the current user to have admin role."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def require_faculty_or_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency that requires faculty or admin role."""
    if current_user.get("role") not in ("faculty", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faculty or admin access required",
        )
    return current_user
