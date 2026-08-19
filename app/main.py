"""FastAPI application entry point: `uvicorn app.main:app`."""

from fastapi import APIRouter, Depends, FastAPI

from app.auth import BearerTokenGuard, require_token
from app.config import get_settings
from app.mcp_server import create_mcp_app
from app.routers import health


def create_app() -> FastAPI:
    """Build the application, failing loudly if required settings are missing."""
    # Read settings before anything is served: an unset PRENGINE_TOKEN must crash
    # the process at boot, never leave routes open.
    get_settings()

    mcp_app = create_mcp_app()

    # The MCP session manager runs in the sub-app's lifespan, which a mount does
    # not start on its own — FastAPI has to own it.
    app = FastAPI(title="PR Engine", version="0.1.0", lifespan=mcp_app.lifespan)

    # Open routes.
    app.include_router(health.router)

    # Everything under /api requires the bearer token.
    api = APIRouter(prefix="/api", dependencies=[Depends(require_token)])
    api.include_router(health.api_router)
    app.include_router(api)

    # A mounted ASGI app bypasses FastAPI's dependencies, so /mcp is guarded at
    # the transport level with the same token check.
    app.mount("/mcp", BearerTokenGuard(mcp_app))

    return app


app = create_app()
