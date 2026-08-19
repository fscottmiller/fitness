"""Bearer token authentication for every non-public route."""

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config import Settings, get_settings

UNAUTHORIZED_DETAIL = "Missing or invalid bearer token"
UNAUTHORIZED_HEADERS = {"WWW-Authenticate": "Bearer"}

# auto_error=False so a missing header lands on our 401 below rather than
# FastAPI's built-in 403 for absent credentials.
bearer_scheme = HTTPBearer(auto_error=False)


def token_is_valid(token: str | None, settings: Settings) -> bool:
    """Return whether `token` is the configured bearer token.

    The single comparison both the route dependency and the ASGI guard go
    through, so /api and /mcp cannot drift apart.
    """
    if token is None:
        return False
    return secrets.compare_digest(token, settings.prengine_token)


def require_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    """Reject the request unless it carries the configured bearer token."""
    if not token_is_valid(
        credentials.credentials if credentials else None,
        settings,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNAUTHORIZED_DETAIL,
            headers=UNAUTHORIZED_HEADERS,
        )


def _bearer_token(authorization: str | None) -> str | None:
    """Pull the credentials out of an `Authorization: Bearer ...` header."""
    if authorization is None:
        return None
    scheme, _, credentials = authorization.partition(" ")
    if scheme.lower() != "bearer" or not credentials:
        return None
    return credentials


class BearerTokenGuard:
    """ASGI middleware applying the same bearer check to a mounted sub-app.

    Mounted ASGI apps never see FastAPI's dependency system, so `/mcp` needs the
    check at the transport level to be guarded at all.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return

        token = _bearer_token(Headers(scope=scope).get("authorization"))
        if not token_is_valid(token, get_settings()):
            await self._reject(scope, receive, send)
            return

        await self.app(scope, receive, send)

    async def _reject(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Refuse the connection, matching /api's 401 body where possible."""
        if scope["type"] == "websocket":
            # 1008 is the policy-violation close code; there is no status line.
            await send({"type": "websocket.close", "code": 1008})
            return

        response = JSONResponse(
            {"detail": UNAUTHORIZED_DETAIL},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers=UNAUTHORIZED_HEADERS,
        )
        await response(scope, receive, send)
