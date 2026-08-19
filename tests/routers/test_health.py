"""Tests for app/routers/health.py."""

from fastapi.testclient import TestClient


def test_health_200_without_token(client: TestClient) -> None:
    """/health is open so a deploy probe needs no secret."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
