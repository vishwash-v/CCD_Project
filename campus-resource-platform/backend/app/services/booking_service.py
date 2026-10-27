"""
Booking service — handles conflict detection and booking logic.
"""

from typing import List, Optional
from datetime import datetime, timezone
from app.services.cloudant_service import db, DB_BOOKINGS, DB_RESOURCES


async def check_booking_conflict(
    resource_id: str, date: str, start_time: str, end_time: str, exclude_booking_id: str = None
) -> Optional[dict]:
    """
    Check if a booking conflicts with existing bookings for the same resource and date.
    
    Returns:
        The conflicting booking document, or None if no conflict.
    """
    # Find all bookings for this resource on this date
    existing_bookings = await db.find_documents(
        DB_BOOKINGS,
        {
            "type": "booking",
            "resource_id": resource_id,
            "date": date,
            "status": {"$in": ["pending", "approved"]},
        },
    )

    for booking in existing_bookings:
        # Skip the booking being updated
        if exclude_booking_id and booking["_id"] == exclude_booking_id:
            continue

        # Check time overlap
        existing_start = booking["start_time"]
        existing_end = booking["end_time"]

        # Two time ranges overlap if one starts before the other ends
        if start_time < existing_end and end_time > existing_start:
            return booking

    return None


async def get_resource_availability(resource_id: str, date: str) -> List[dict]:
    """
    Get all booked time slots for a resource on a specific date.
    
    Returns:
        List of booked time slots with start_time, end_time, and status.
    """
    bookings = await db.find_documents(
        DB_BOOKINGS,
        {
            "type": "booking",
            "resource_id": resource_id,
            "date": date,
            "status": {"$in": ["pending", "approved"]},
        },
    )
    return [
        {
            "start_time": b["start_time"],
            "end_time": b["end_time"],
            "status": b["status"],
            "booked_by": b.get("user_name", "Unknown"),
        }
        for b in bookings
    ]


async def get_utilization_stats(days: int = 30) -> dict:
    """
    Calculate resource utilization statistics over the past N days.
    
    Returns:
        Dict with overall stats, per-resource stats, and peak hours.
    """
    from datetime import timedelta

    today = datetime.now(timezone.utc).date()
    start_date = (today - timedelta(days=days)).isoformat()
    end_date = today.isoformat()

    # Get all bookings in the date range
    all_bookings = await db.find_documents(
        DB_BOOKINGS,
        {
            "type": "booking",
            "date": {"$gte": start_date, "$lte": end_date},
        },
    )

    # Get all resources
    all_resources = await db.get_all_documents(DB_RESOURCES, doc_type="resource")

    # Calculate per-resource utilization
    resource_stats = {}
    hour_counts = {str(h).zfill(2): 0 for h in range(6, 22)}  # 6 AM to 10 PM

    for resource in all_resources:
        rid = resource["_id"]
        resource_bookings = [b for b in all_bookings if b["resource_id"] == rid]
        total_hours = sum(_calc_hours(b["start_time"], b["end_time"]) for b in resource_bookings)
        # Available hours = 16 hours/day * days
        available_hours = 16 * days
        utilization = round((total_hours / available_hours) * 100, 1) if available_hours > 0 else 0

        resource_stats[rid] = {
            "name": resource["name"],
            "category": resource["category"],
            "total_bookings": len(resource_bookings),
            "total_hours_used": round(total_hours, 1),
            "utilization_percent": utilization,
        }

    # Calculate peak hours
    for booking in all_bookings:
        start_h = int(booking["start_time"].split(":")[0])
        end_h = int(booking["end_time"].split(":")[0])
        for h in range(start_h, end_h):
            key = str(h).zfill(2)
            if key in hour_counts:
                hour_counts[key] += 1

    # Status breakdown
    status_counts = {}
    for b in all_bookings:
        status = b.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "period_days": days,
        "total_bookings": len(all_bookings),
        "total_resources": len(all_resources),
        "status_breakdown": status_counts,
        "resource_utilization": resource_stats,
        "peak_hours": hour_counts,
    }


def _calc_hours(start_time: str, end_time: str) -> float:
    """Calculate the number of hours between two HH:MM time strings."""
    start_parts = start_time.split(":")
    end_parts = end_time.split(":")
    start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
    end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])
    return max(0, (end_minutes - start_minutes) / 60)
