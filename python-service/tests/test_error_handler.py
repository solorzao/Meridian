"""Tests for the global exception handler middleware."""

import json

import pytest
from fastapi import Request
from unittest.mock import MagicMock

from app.middleware.error_handler import global_exception_handler


def _make_fake_request() -> Request:
    """Create a minimal fake ASGI request object."""
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        "query_string": b"",
        "headers": [],
    }
    return Request(scope)


@pytest.mark.asyncio
async def test_value_error_returns_400():
    """ValueError should map to HTTP 400 with the exception message."""
    request = _make_fake_request()
    exc = ValueError("Invalid input data")

    response = await global_exception_handler(request, exc)

    assert response.status_code == 400
    body = json.loads(response.body)
    assert body["error"] == "Invalid input data"
    assert body["statusCode"] == 400
    assert "timestamp" in body


@pytest.mark.asyncio
async def test_key_error_returns_404():
    """KeyError should map to HTTP 404 with the key as message."""
    request = _make_fake_request()
    exc = KeyError("resource_id")

    response = await global_exception_handler(request, exc)

    assert response.status_code == 404
    body = json.loads(response.body)
    assert body["statusCode"] == 404
    assert "timestamp" in body


@pytest.mark.asyncio
async def test_permission_error_returns_401():
    """PermissionError should map to HTTP 401 with 'Unauthorized'."""
    request = _make_fake_request()
    exc = PermissionError("access denied")

    response = await global_exception_handler(request, exc)

    assert response.status_code == 401
    body = json.loads(response.body)
    assert body["error"] == "Unauthorized"
    assert body["statusCode"] == 401
    assert "timestamp" in body


@pytest.mark.asyncio
async def test_generic_exception_returns_500():
    """Any unhandled exception should map to HTTP 500 with generic message."""
    request = _make_fake_request()
    exc = RuntimeError("something broke")

    response = await global_exception_handler(request, exc)

    assert response.status_code == 500
    body = json.loads(response.body)
    assert body["error"] == "An unexpected error occurred"
    assert body["statusCode"] == 500
    assert "timestamp" in body
