"""
Notification service — sends booking notifications.
Uses simple logging for now; can be extended to email/push notifications.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# In-app notification store (in production, this would go to a database or message queue)
_notifications: list = []


class NotificationService:
    """Handles sending notifications for booking events."""

    @staticmethod
    async def notify_booking_created(booking: dict, user: dict):
        """Notify user that their booking request has been created."""
        notification = {
            "user_id": user.get("_id"),
            "type": "booking_created",
            "title": "Booking Request Submitted",
            "message": f"Your booking for {booking.get('resource_name', 'a resource')} "
                       f"on {booking['date']} ({booking['start_time']}-{booking['end_time']}) "
                       f"has been submitted and is pending approval.",
            "read": False,
        }
        _notifications.append(notification)
        logger.info(f"[NOTIFICATION] Booking created: {notification['message']}")

    @staticmethod
    async def notify_booking_approved(booking: dict):
        """Notify user that their booking has been approved."""
        notification = {
            "user_id": booking.get("user_id"),
            "type": "booking_approved",
            "title": "Booking Approved ✅",
            "message": f"Your booking for {booking.get('resource_name', 'a resource')} "
                       f"on {booking['date']} ({booking['start_time']}-{booking['end_time']}) "
                       f"has been approved!",
            "read": False,
        }
        _notifications.append(notification)
        logger.info(f"[NOTIFICATION] Booking approved: {notification['message']}")

    @staticmethod
    async def notify_booking_rejected(booking: dict, reason: Optional[str] = None):
        """Notify user that their booking has been rejected."""
        msg = (
            f"Your booking for {booking.get('resource_name', 'a resource')} "
            f"on {booking['date']} has been rejected."
        )
        if reason:
            msg += f" Reason: {reason}"

        notification = {
            "user_id": booking.get("user_id"),
            "type": "booking_rejected",
            "title": "Booking Rejected ❌",
            "message": msg,
            "read": False,
        }
        _notifications.append(notification)
        logger.info(f"[NOTIFICATION] Booking rejected: {notification['message']}")

    @staticmethod
    async def notify_booking_cancelled(booking: dict):
        """Notify relevant parties about a booking cancellation."""
        notification = {
            "user_id": booking.get("user_id"),
            "type": "booking_cancelled",
            "title": "Booking Cancelled",
            "message": f"Booking for {booking.get('resource_name', 'a resource')} "
                       f"on {booking['date']} has been cancelled.",
            "read": False,
        }
        _notifications.append(notification)
        logger.info(f"[NOTIFICATION] Booking cancelled: {notification['message']}")

    @staticmethod
    async def get_user_notifications(user_id: str) -> list:
        """Get all notifications for a specific user."""
        return [n for n in _notifications if n.get("user_id") == user_id]

    @staticmethod
    async def mark_as_read(user_id: str):
        """Mark all notifications for a user as read."""
        for n in _notifications:
            if n.get("user_id") == user_id:
                n["read"] = True


notifications = NotificationService()
