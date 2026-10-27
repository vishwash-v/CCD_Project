"""
Pydantic models for User operations.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"


class UserSignup(BaseModel):
    """Request model for user registration."""
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole = UserRole.STUDENT
    department: str = Field(default="", max_length=100)


class UserLogin(BaseModel):
    """Request model for user login."""
    email: str
    password: str


class UserResponse(BaseModel):
    """Response model for user data (no password)."""
    id: str
    name: str
    email: str
    role: str
    department: str
    created_at: str


class UserUpdate(BaseModel):
    """Request model for updating user profile."""
    name: Optional[str] = None
    department: Optional[str] = None


class TokenResponse(BaseModel):
    """Response model for authentication token."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
