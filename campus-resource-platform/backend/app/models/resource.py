"""
Pydantic models for Resource operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ResourceCategory(str, Enum):
    HALL = "hall"
    LAB = "lab"
    EQUIPMENT = "equipment"
    FACILITY = "facility"
    CLASSROOM = "classroom"
    SPORTS = "sports"


class ResourceCreate(BaseModel):
    """Request model for creating a new resource."""
    name: str = Field(..., min_length=2, max_length=200)
    category: ResourceCategory
    location: str = Field(..., min_length=2, max_length=200)
    capacity: int = Field(default=0, ge=0)
    amenities: List[str] = Field(default_factory=list)
    description: str = Field(default="", max_length=500)
    image_url: str = Field(default="")


class ResourceUpdate(BaseModel):
    """Request model for updating a resource."""
    name: Optional[str] = None
    category: Optional[ResourceCategory] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    amenities: Optional[List[str]] = None
    description: Optional[str] = None
    available: Optional[bool] = None
    image_url: Optional[str] = None


class ResourceResponse(BaseModel):
    """Response model for resource data."""
    id: str
    name: str
    category: str
    location: str
    capacity: int
    amenities: List[str]
    description: str
    available: bool
    image_url: str
    created_by: str
    created_at: str
