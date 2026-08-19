"""FastAPI application entry point: `uvicorn app.main:app`."""

from fastapi import APIRouter, Depends, FastAPI

from app.auth import require_token
from app.config import get_settings
from app.routers import health


def create_app() -> FastAPI:
    """Build the application, failing loudly if required settings are missing."""
    # Read settings before anything is served: an unset PRENGINE_TOKEN must crash
    # the process at boot, never leave routes open.
    get_settings()

    app = FastAPI(title="PR Engine", version="0.1.0")

    # Open routes.
    app.include_router(health.router)

    # Everything under /api requires the bearer token. /mcp gets the same
    # dependency when the MCP server is mounted.
    api = APIRouter(prefix="/api", dependencies=[Depends(require_token)])
    api.include_router(health.api_router)
    app.include_router(api)

    return app


app = create_app()
