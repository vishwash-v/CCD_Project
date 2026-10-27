"""
Pydantic models for Booking operations.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class BookingCreate(BaseModel):
    """Request model for creating a new booking."""
    resource_id: str = Field(..., min_length=1)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")  # HH:MM
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")    # HH:MM
    purpose: str = Field(default="", max_length=500)


class BookingUpdate(BaseModel):
    """Request model for updating a booking."""
    date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    end_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    purpose: Optional[str] = None


class BookingApproval(BaseModel):
    """Request model for approving/rejecting a booking."""
    status: BookingStatus
    reason: Optional[str] = None


class BookingResponse(BaseModel):
    """Response model for booking data."""
    id: str
    resource_id: str
    resource_name: str
    user_id: str
    user_name: str
    date: str
    start_time: str
    end_time: str
    purpose: str
    status: str
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: str
