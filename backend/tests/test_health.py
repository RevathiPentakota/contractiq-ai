"""Tests for GET /api/v1/health."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_200() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_check_response_body() -> None:
    response = client.get("/api/v1/health")
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "ContractIQ AI API"
    assert "version" in body
