"""Database engine, connection pragmas, and the request-scoped session dependency."""

from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session

from app.config import get_settings

PRAGMAS: dict[str, str | int] = {
    # Readers don't block the writer, and the writer doesn't block readers.
    "journal_mode": "WAL",
    # Wait up to 5s for a competing writer instead of failing instantly.
    "busy_timeout": 5000,
    # SQLite disables foreign key enforcement per connection by default.
    "foreign_keys": "ON",
    # Durable against a process crash under WAL; only power loss can lose a commit.
    "synchronous": "NORMAL",
}


def _apply_pragmas(dbapi_connection: Any, _connection_record: Any) -> None:
    """Apply `PRAGMAS` to a freshly opened connection.

    Pragmas are per-connection in SQLite, so they have to be set every time a new
    connection is opened, not once when the engine is built.
    """
    cursor = dbapi_connection.cursor()
    try:
        for pragma, value in PRAGMAS.items():
            cursor.execute(f"PRAGMA {pragma}={value}")
    finally:
        cursor.close()


def database_url(database_path: Path) -> str:
    """Return the SQLAlchemy URL for a SQLite file at `database_path`."""
    return f"sqlite:///{database_path}"


def create_db_engine(url: str) -> Engine:
    """Build an engine for `url` with the pragmas wired up."""
    engine = create_engine(url, future=True)
    event.listen(engine, "connect", _apply_pragmas)
    return engine


@lru_cache
def get_engine() -> Engine:
    """Return the process-wide engine, building it on first use."""
    return create_db_engine(database_url(get_settings().database_path))


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a session that closes with the request."""
    with Session(get_engine(), expire_on_commit=False) as session:
        yield session
