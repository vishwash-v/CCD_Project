"""
Unit tests for authentication service and routes.
"""

import pytest
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_access_token


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password_returns_hash(self):
        password = "mysecurepassword"
        hashed = hash_password(password)
        assert hashed != password
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        password = "samepassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # bcrypt uses random salt


class TestJWT:
    """Test JWT token creation and validation."""

    def test_create_and_decode_token(self):
        data = {"sub": "user123", "role": "student"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["role"] == "student"

    def test_decode_invalid_token(self):
        decoded = decode_access_token("invalid.token.here")
        assert decoded is None

    def test_token_contains_expiration(self):
        data = {"sub": "user456"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        assert "exp" in decoded
