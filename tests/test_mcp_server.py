"""Tests for app/mcp_server.py and the guard on its mount."""

import asyncio
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.auth import BearerTokenGuard

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

# Streamable HTTP opens the SSE stream with GET and tears the session down with
# DELETE, so every method has to be covered — those two are the ones a later
# special case would most plausibly wave through.
MCP_METHODS = ["GET", "POST", "DELETE"]


@pytest.mark.parametrize("method", MCP_METHODS)
def test_mcp_401_without_token(client: TestClient, method: str) -> None:
    """A mount bypasses FastAPI dependencies, so this is the guard's own 401."""
    response = client.request(method, "/mcp/", headers=MCP_HEADERS)

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid bearer token"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize("method", MCP_METHODS)
def test_mcp_401_with_wrong_token(client: TestClient, method: str) -> None:
    """A token that is not the configured one is rejected."""
    response = client.request(
        method,
        "/mcp/",
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


def test_mcp_401_closes_unauthenticated_websocket() -> None:
    """A websocket scope is refused too, with a close frame rather than a 401."""
    sent: list[dict[str, Any]] = []

    async def unreachable(*_args: Any) -> None:  # pragma: no cover - never called
        raise AssertionError("the guard let an unauthenticated websocket through")

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    async def receive() -> dict[str, Any]:  # pragma: no cover - never called
        raise AssertionError("the guard read from an unauthenticated websocket")

    guard = BearerTokenGuard(unreachable)
    scope: dict[str, Any] = {"type": "websocket", "path": "/mcp/", "headers": []}
    asyncio.run(guard(scope, receive, send))

    # 1008 is the policy-violation close code.
    assert sent == [{"type": "websocket.close", "code": 1008}]


def test_mcp_initializes_with_valid_token(auth_client: TestClient) -> None:
    """The token gets through and the MCP handshake completes."""
    response = auth_client.post("/mcp/", json=INITIALIZE, headers=MCP_HEADERS)

    assert response.status_code == 200
    # Streamable HTTP answers with SSE; the payload is the JSON-RPC result.
    assert '"result"' in response.text
    assert "serverInfo" in response.text


def test_mcp_accepts_case_insensitive_scheme(client: TestClient, token: str) -> None:
    """The auth scheme is case-insensitive per RFC 7235; the token is not."""
    response = client.post(
        "/mcp/",
        json=INITIALIZE,
        headers={**MCP_HEADERS, "Authorization": f"BEARER {token}"},
    )

    assert response.status_code == 200
