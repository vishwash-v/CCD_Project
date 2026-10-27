"""
Unit tests for booking service — conflict detection and utilization.
"""

import pytest
from app.services.booking_service import _calc_hours


class TestCalcHours:
    """Test time calculation utility."""

    def test_one_hour(self):
        assert _calc_hours("10:00", "11:00") == 1.0

    def test_two_hours(self):
        assert _calc_hours("09:00", "11:00") == 2.0

    def test_half_hour(self):
        assert _calc_hours("10:00", "10:30") == 0.5

    def test_full_day(self):
        assert _calc_hours("06:00", "22:00") == 16.0

    def test_same_time(self):
        assert _calc_hours("10:00", "10:00") == 0.0

    def test_ninety_minutes(self):
        assert _calc_hours("14:00", "15:30") == 1.5
