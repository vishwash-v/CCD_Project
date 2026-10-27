"""
Resource management routes — CRUD for campus resources.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime, timezone
from typing import Optional, List
from app.models.resource import ResourceCreate, ResourceUpdate, ResourceResponse, ResourceCategory
from app.services.cloudant_service import db, DB_RESOURCES
from app.middleware.auth_middleware import get_current_user, require_admin

router = APIRouter(prefix="/api/resources", tags=["Resources"])


@router.get("/", response_model=List[ResourceResponse])
async def list_resources(
    category: Optional[ResourceCategory] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """List all resources, optionally filtered by category or search term."""
    resources = await db.get_all_documents(DB_RESOURCES, doc_type="resource")

    # Filter by category
    if category:
        resources = [r for r in resources if r.get("category") == category.value]

    # Filter by search term
    if search:
        search_lower = search.lower()
        resources = [
            r
            for r in resources
            if search_lower in r.get("name", "").lower()
            or search_lower in r.get("location", "").lower()
            or search_lower in r.get("description", "").lower()
        ]

    return [
        ResourceResponse(
            id=r["_id"],
            name=r["name"],
            category=r["category"],
            location=r["location"],
            capacity=r.get("capacity", 0),
            amenities=r.get("amenities", []),
            description=r.get("description", ""),
            available=r.get("available", True),
            image_url=r.get("image_url", ""),
            created_by=r.get("created_by", ""),
            created_at=r.get("created_at", ""),
        )
        for r in resources
    ]


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: str, current_user: dict = Depends(get_current_user)
):
    """Get a single resource by ID."""
    resource = await db.get_document(DB_RESOURCES, resource_id)
    if not resource or resource.get("type") != "resource":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    return ResourceResponse(
        id=resource["_id"],
        name=resource["name"],
        category=resource["category"],
        location=resource["location"],
        capacity=resource.get("capacity", 0),
        amenities=resource.get("amenities", []),
        description=resource.get("description", ""),
        available=resource.get("available", True),
        image_url=resource.get("image_url", ""),
        created_by=resource.get("created_by", ""),
        created_at=resource.get("created_at", ""),
    )


@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource_data: ResourceCreate,
    current_user: dict = Depends(require_admin),
):
    """Create a new campus resource (admin only)."""
    now = datetime.now(timezone.utc).isoformat()
    resource_doc = {
        "type": "resource",
        "name": resource_data.name,
        "category": resource_data.category.value,
        "location": resource_data.location,
        "capacity": resource_data.capacity,
        "amenities": resource_data.amenities,
        "description": resource_data.description,
        "image_url": resource_data.image_url,
        "available": True,
        "created_by": current_user["_id"],
        "created_at": now,
    }

    created = await db.create_document(DB_RESOURCES, resource_doc)

    return ResourceResponse(
        id=created["_id"],
        name=created["name"],
        category=created["category"],
        location=created["location"],
        capacity=created.get("capacity", 0),
        amenities=created.get("amenities", []),
        description=created.get("description", ""),
        available=created.get("available", True),
        image_url=created.get("image_url", ""),
        created_by=created.get("created_by", ""),
        created_at=created.get("created_at", ""),
    )


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: str,
    updates: ResourceUpdate,
    current_user: dict = Depends(require_admin),
):
    """Update a resource (admin only)."""
    resource = await db.get_document(DB_RESOURCES, resource_id)
    if not resource or resource.get("type") != "resource":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    update_data = updates.model_dump(exclude_unset=True)
    if "category" in update_data and update_data["category"]:
        update_data["category"] = update_data["category"].value

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    updated = await db.update_document(DB_RESOURCES, resource_id, update_data)

    return ResourceResponse(
        id=updated["_id"],
        name=updated["name"],
        category=updated["category"],
        location=updated["location"],
        capacity=updated.get("capacity", 0),
        amenities=updated.get("amenities", []),
        description=updated.get("description", ""),
        available=updated.get("available", True),
        image_url=updated.get("image_url", ""),
        created_by=updated.get("created_by", ""),
        created_at=updated.get("created_at", ""),
    )


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: str,
    current_user: dict = Depends(require_admin),
):
    """Delete a resource (admin only)."""
    success = await db.delete_document(DB_RESOURCES, resource_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )
