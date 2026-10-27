"""
Unit tests for resource models.
"""

import pytest
from pydantic import ValidationError
from app.models.resource import ResourceCreate, ResourceCategory


class TestResourceModels:
    """Test resource Pydantic model validation."""

    def test_valid_resource_creation(self):
        resource = ResourceCreate(
            name="Test Lab",
            category=ResourceCategory.LAB,
            location="Block A, Floor 1",
            capacity=40,
            amenities=["computers", "AC"],
            description="A test lab",
        )
        assert resource.name == "Test Lab"
        assert resource.category == ResourceCategory.LAB

    def test_resource_name_too_short(self):
        with pytest.raises(ValidationError):
            ResourceCreate(
                name="A",  # min_length=2
                category=ResourceCategory.LAB,
                location="Block A",
            )

    def test_resource_default_values(self):
        resource = ResourceCreate(
            name="Test Room",
            category=ResourceCategory.CLASSROOM,
            location="Block B",
        )
        assert resource.capacity == 0
        assert resource.amenities == []
        assert resource.description == ""

    def test_all_categories_valid(self):
        for category in ResourceCategory:
            resource = ResourceCreate(
                name="Test",
                category=category,
                location="Location",
            )
            assert resource.category == category
