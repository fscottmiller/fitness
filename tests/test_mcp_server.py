"""Tests for app/mcp_server.py and the guard on its mount."""

from typing import Any

from fastapi.testclient import TestClient

MCP_HEADERS = {"Accept": "application/json, text/event-stream"}
INITIALIZE: dict[str, Any] = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "tests", "version": "1"},
    },
}


def test_mcp_401_without_token(client: TestClient) -> None:
    """A mount bypasses FastAPI dependencies, so this is the guard's own 401."""
    response = client.post("/mcp/", json=INITIALIZE, headers=MCP_HEADERS)

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid bearer token"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_mcp_401_with_wrong_token(client: TestClient) -> None:
    """A token that is not the configured one is rejected."""
    response = client.post(
        "/mcp/",
        json=INITIALIZE,
        headers={**MCP_HEADERS, "Authorization": "Bearer nope"},
    )

    assert response.status_code == 401


def test_mcp_401_with_non_bearer_scheme(client: TestClient) -> None:
    """Credentials under another scheme are not mistaken for the token."""
    response = client.post(
        "/mcp/",
        json=INITIALIZE,
        headers={**MCP_HEADERS, "Authorization": "Basic test-token"},
    )

    assert response.status_code == 401


def test_mcp_401_without_trailing_slash(client: TestClient) -> None:
    """/mcp is guarded before the mount's redirect to /mcp/ can happen."""
    response = client.post("/mcp", json=INITIALIZE, headers=MCP_HEADERS)

    assert response.status_code == 401


def test_mcp_initializes_with_valid_token(auth_client: TestClient) -> None:
    """The token gets through and the MCP handshake completes."""
    response = auth_client.post("/mcp/", json=INITIALIZE, headers=MCP_HEADERS)

    assert response.status_code == 200
    # Streamable HTTP answers with SSE; the payload is the JSON-RPC result.
    assert '"result"' in response.text
    assert "serverInfo" in response.text
