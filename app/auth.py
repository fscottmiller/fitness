"""Bearer token authentication for every non-public route."""

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings

# auto_error=False so a missing header lands on our 401 below rather than
# FastAPI's built-in 403 for absent credentials.
bearer_scheme = HTTPBearer(auto_error=False)


def require_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    """Reject the request unless it carries the configured bearer token."""
    if credentials is None or not secrets.compare_digest(
        credentials.credentials, settings.prengine_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
