"""Application settings.

`Settings` is the single place environment configuration enters the app. No other
module calls `os.getenv` — if a value is needed somewhere, it is added here first.
Required values have no default, so a missing one raises at boot rather than
silently degrading (an unset token must never mean "authenticate everyone").
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed configuration, read once at startup."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    prengine_token: str
    """Bearer token guarding every /api and /mcp route. Required."""

    database_path: Path = Path("prengine.db")
    """Filesystem path of the SQLite database file."""

    hevy_api_key: str | None = None
    """Hevy API key. Optional: nothing calls Hevy in this milestone."""


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings, constructing them on first use."""
    return Settings()
