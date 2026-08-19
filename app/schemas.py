"""Pydantic request/response schemas, kept separate from the ORM on purpose."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Body of `GET /health` and `GET /api/ping`."""

    status: Literal["ok"]
