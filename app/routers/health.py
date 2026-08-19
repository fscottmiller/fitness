"""Liveness routes: one open, one behind the bearer token."""

from fastapi import APIRouter

from app.schemas import HealthResponse

router = APIRouter(tags=["health"])
"""Mounted at the root, deliberately unauthenticated."""

api_router = APIRouter(tags=["health"])
"""Mounted under /api, so it inherits the bearer-token dependency."""


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report that the process is up. Open so a deploy probe needs no secret."""
    return HealthResponse(status="ok")


@api_router.get("/ping", response_model=HealthResponse)
def ping() -> HealthResponse:
    """Same answer as /health, but proves a token is accepted end to end."""
    return HealthResponse(status="ok")
