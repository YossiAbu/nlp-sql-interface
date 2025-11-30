# backend/tests/__init__.py
"""Test helpers for DRY test code."""
from typing import Dict
from httpx import ASGITransport


def make_user_payload(
    full_name: str = "Test User",
    email: str = "test@example.com",
    password: str = "TestPass123!"
) -> Dict[str, str]:
    """Create a user registration payload."""
    return {
        "full_name": full_name,
        "email": email,
        "password": password
    }


def make_login_payload(
    email: str = "test@example.com",
    password: str = "TestPass123!"
) -> Dict[str, str]:
    """Create a login payload."""
    return {
        "email": email,
        "password": password
    }


def get_test_client(app) -> tuple:
    """Create ASGITransport and return (transport, base_url) for AsyncClient."""
    return ASGITransport(app=app), "http://test"

