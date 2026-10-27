"""
Booking routes — create, manage, approve/reject bookings.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime, timezone
from typing import Optional, List
from app.models.booking import BookingCreate, BookingUpdate, BookingApproval, BookingResponse, BookingStatus
from app.services.cloudant_service import db, DB_BOOKINGS, DB_RESOURCES
from app.services.booking_service import check_booking_conflict, get_resource_availability
from app.services.notification_service import notifications
from app.middleware.auth_middleware import get_current_user, require_admin, require_faculty_or_admin

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


def _format_booking(booking: dict) -> BookingResponse:
    """Convert a booking document to a response model."""
    return BookingResponse(
        id=booking["_id"],
        resource_id=booking["resource_id"],
        resource_name=booking.get("resource_name", "Unknown"),
        user_id=booking["user_id"],
        user_name=booking.get("user_name", "Unknown"),
        date=booking["date"],
        start_time=booking["start_time"],
        end_time=booking["end_time"],
        purpose=booking.get("purpose", ""),
        status=booking["status"],
        approved_by=booking.get("approved_by"),
        rejection_reason=booking.get("rejection_reason"),
        created_at=booking.get("created_at", ""),
    )


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new booking request."""
    # Validate time range
    if booking_data.start_time >= booking_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

    # Check resource exists
    resource = await db.get_document(DB_RESOURCES, booking_data.resource_id)
    if not resource or resource.get("type") != "resource":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    if not resource.get("available", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource is currently unavailable",
        )

    # Check for conflicts
    conflict = await check_booking_conflict(
        booking_data.resource_id,
        booking_data.date,
        booking_data.start_time,
        booking_data.end_time,
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Time slot conflicts with an existing booking "
                   f"({conflict['start_time']}-{conflict['end_time']})",
        )

    # Create booking document
    now = datetime.now(timezone.utc).isoformat()
    booking_doc = {
        "type": "booking",
        "resource_id": booking_data.resource_id,
        "resource_name": resource["name"],
        "user_id": current_user["_id"],
        "user_name": current_user["name"],
        "date": booking_data.date,
        "start_time": booking_data.start_time,
        "end_time": booking_data.end_time,
        "purpose": booking_data.purpose,
        "status": "pending",
        "created_at": now,
    }

    created = await db.create_document(DB_BOOKINGS, booking_doc)

    # Send notification
    await notifications.notify_booking_created(created, current_user)

    return _format_booking(created)


@router.get("/", response_model=List[BookingResponse])
async def list_bookings(
    status_filter: Optional[BookingStatus] = Query(None, alias="status"),
    resource_id: Optional[str] = None,
    date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    List bookings.
    - Students see their own bookings
    - Faculty see their own bookings
    - Admins see all bookings
    """
    if current_user.get("role") == "admin":
        bookings = await db.get_all_documents(DB_BOOKINGS, doc_type="booking")
    else:
        bookings = await db.find_documents(
            DB_BOOKINGS,
            {"type": "booking", "user_id": current_user["_id"]},
        )

    # Apply filters
    if status_filter:
        bookings = [b for b in bookings if b.get("status") == status_filter.value]
    if resource_id:
        bookings = [b for b in bookings if b.get("resource_id") == resource_id]
    if date:
        bookings = [b for b in bookings if b.get("date") == date]

    # Sort by date descending
    bookings.sort(key=lambda b: (b.get("date", ""), b.get("start_time", "")), reverse=True)

    return [_format_booking(b) for b in bookings]


@router.get("/availability/{resource_id}")
async def check_availability(
    resource_id: str,
    date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: dict = Depends(get_current_user),
):
    """Get booked time slots for a resource on a specific date."""
    # Check resource exists
    resource = await db.get_document(DB_RESOURCES, resource_id)
    if not resource or resource.get("type") != "resource":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    slots = await get_resource_availability(resource_id, date)
    return {
        "resource_id": resource_id,
        "resource_name": resource["name"],
        "date": date,
        "booked_slots": slots,
    }


@router.get("/all", response_model=List[BookingResponse])
async def list_all_bookings(
    status_filter: Optional[BookingStatus] = Query(None, alias="status"),
    current_user: dict = Depends(require_admin),
):
    """List all bookings across all users (admin only)."""
    bookings = await db.get_all_documents(DB_BOOKINGS, doc_type="booking")

    if status_filter:
        bookings = [b for b in bookings if b.get("status") == status_filter.value]

    bookings.sort(key=lambda b: b.get("created_at", ""), reverse=True)
    return [_format_booking(b) for b in bookings]


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific booking by ID."""
    booking = await db.get_document(DB_BOOKINGS, booking_id)
    if not booking or booking.get("type") != "booking":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    # Only allow access to own bookings (unless admin)
    if (
        current_user.get("role") != "admin"
        and booking["user_id"] != current_user["_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return _format_booking(booking)


@router.put("/{booking_id}/approve", response_model=BookingResponse)
async def approve_or_reject_booking(
    booking_id: str,
    approval: BookingApproval,
    current_user: dict = Depends(require_faculty_or_admin),
):
    """Approve or reject a booking (faculty/admin only)."""
    booking = await db.get_document(DB_BOOKINGS, booking_id)
    if not booking or booking.get("type") != "booking":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking is already {booking['status']}",
        )

    update_data = {
        "status": approval.status.value,
        "approved_by": current_user["_id"],
    }
    if approval.reason:
        update_data["rejection_reason"] = approval.reason

    updated = await db.update_document(DB_BOOKINGS, booking_id, update_data)

    # Send notification
    if approval.status == BookingStatus.APPROVED:
        await notifications.notify_booking_approved(updated)
    elif approval.status == BookingStatus.REJECTED:
        await notifications.notify_booking_rejected(updated, approval.reason)

    return _format_booking(updated)


@router.put("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Cancel a booking (own booking or admin)."""
    booking = await db.get_document(DB_BOOKINGS, booking_id)
    if not booking or booking.get("type") != "booking":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if (
        current_user.get("role") != "admin"
        and booking["user_id"] != current_user["_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    if booking["status"] == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled",
        )

    updated = await db.update_document(
        DB_BOOKINGS, booking_id, {"status": "cancelled"}
    )
    await notifications.notify_booking_cancelled(updated)

    return _format_booking(updated)


@router.get("/notifications/mine")
async def get_my_notifications(current_user: dict = Depends(get_current_user)):
    """Get notifications for the current user."""
    user_notifications = await notifications.get_user_notifications(current_user["_id"])
    return {"notifications": user_notifications}


@router.put("/notifications/read")
async def mark_notifications_read(current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read."""
    await notifications.mark_as_read(current_user["_id"])
    return {"message": "Notifications marked as read"}
