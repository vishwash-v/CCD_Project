"""
Analytics routes — utilization stats and dashboards.
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.booking_service import get_utilization_stats
from app.services.cloudant_service import db, DB_BOOKINGS, DB_RESOURCES, DB_USERS
from app.middleware.auth_middleware import get_current_user, require_faculty_or_admin

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """
    Get dashboard overview stats.
    Available to all authenticated users (students see limited data).
    """
    # Count totals
    all_resources = await db.get_all_documents(DB_RESOURCES, doc_type="resource")
    all_bookings = await db.get_all_documents(DB_BOOKINGS, doc_type="booking")

    if current_user.get("role") == "admin":
        all_users = await db.get_all_documents(DB_USERS, doc_type="user")
        total_users = len(all_users)
    else:
        total_users = None

    # Calculate booking status counts
    pending_count = len([b for b in all_bookings if b.get("status") == "pending"])
    approved_count = len([b for b in all_bookings if b.get("status") == "approved"])
    rejected_count = len([b for b in all_bookings if b.get("status") == "rejected"])

    # My bookings count (for non-admins)
    my_bookings = len(
        [b for b in all_bookings if b.get("user_id") == current_user["_id"]]
    )

    # Category distribution
    category_counts = {}
    for r in all_resources:
        cat = r.get("category", "other")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return {
        "total_resources": len(all_resources),
        "total_bookings": len(all_bookings),
        "total_users": total_users,
        "my_bookings": my_bookings,
        "pending_bookings": pending_count,
        "approved_bookings": approved_count,
        "rejected_bookings": rejected_count,
        "resource_categories": category_counts,
    }


@router.get("/utilization")
async def get_utilization(
    days: int = Query(default=30, ge=1, le=365),
    current_user: dict = Depends(require_faculty_or_admin),
):
    """
    Get detailed utilization analytics (faculty/admin only).
    Shows resource usage patterns over a specified period.
    """
    stats = await get_utilization_stats(days)
    return stats


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    """Get recent booking activity."""
    if current_user.get("role") == "admin":
        bookings = await db.get_all_documents(DB_BOOKINGS, doc_type="booking")
    else:
        bookings = await db.find_documents(
            DB_BOOKINGS,
            {"type": "booking", "user_id": current_user["_id"]},
        )

    # Sort by created_at descending and limit
    bookings.sort(key=lambda b: b.get("created_at", ""), reverse=True)
    recent = bookings[:limit]

    return {
        "activities": [
            {
                "id": b["_id"],
                "resource_name": b.get("resource_name", "Unknown"),
                "user_name": b.get("user_name", "Unknown"),
                "date": b["date"],
                "start_time": b["start_time"],
                "end_time": b["end_time"],
                "status": b["status"],
                "created_at": b.get("created_at", ""),
            }
            for b in recent
        ]
    }
