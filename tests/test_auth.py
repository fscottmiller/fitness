"""Tests for app/auth.py, exercised through an /api route."""

from fastapi.testclient import TestClient


def test_api_401_without_token(client: TestClient) -> None:
    """A missing Authorization header is a 401, not a 403."""
    response = client.get("/api/ping")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_api_401_with_wrong_token(client: TestClient) -> None:
    """A token that is not the configured one is rejected."""
    response = client.get("/api/ping", headers={"Authorization": "Bearer nope"})

    assert response.status_code == 401


def test_api_200_with_valid_token(auth_client: TestClient) -> None:
    """The configured token gets through."""
    response = auth_client.get("/api/ping")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
