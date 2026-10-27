"""
Authentication routes — signup, login, profile management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from app.models.user import UserSignup, UserLogin, UserResponse, TokenResponse, UserUpdate
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.services.cloudant_service import db, DB_USERS
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    """Register a new user account."""
    # Check if email already exists
    existing = await db.find_documents(
        DB_USERS, {"type": "user", "email": user_data.email}
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Create user document
    now = datetime.now(timezone.utc).isoformat()
    user_doc = {
        "type": "user",
        "name": user_data.name,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "role": user_data.role.value,
        "department": user_data.department,
        "created_at": now,
    }

    created_user = await db.create_document(DB_USERS, user_doc)

    # Generate JWT token
    token = create_access_token(
        data={"sub": created_user["_id"], "role": created_user["role"]}
    )

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=created_user["_id"],
            name=created_user["name"],
            email=created_user["email"],
            role=created_user["role"],
            department=created_user["department"],
            created_at=created_user["created_at"],
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Log in with email and password."""
    # Find user by email
    users = await db.find_documents(
        DB_USERS, {"type": "user", "email": credentials.email}
    )
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user = users[0]

    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate JWT token
    token = create_access_token(
        data={"sub": user["_id"], "role": user["role"]}
    )

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user["_id"],
            name=user["name"],
            email=user["email"],
            role=user["role"],
            department=user["department"],
            created_at=user["created_at"],
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get the current user's profile."""
    return UserResponse(
        id=current_user["_id"],
        name=current_user["name"],
        email=current_user["email"],
        role=current_user["role"],
        department=current_user.get("department", ""),
        created_at=current_user["created_at"],
    )


@router.put("/me", response_model=UserResponse)
async def update_profile(
    updates: UserUpdate, current_user: dict = Depends(get_current_user)
):
    """Update the current user's profile."""
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    updated = await db.update_document(DB_USERS, current_user["_id"], update_data)

    return UserResponse(
        id=updated["_id"],
        name=updated["name"],
        email=updated["email"],
        role=updated["role"],
        department=updated.get("department", ""),
        created_at=updated["created_at"],
    )
