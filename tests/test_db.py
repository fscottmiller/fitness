"""Tests for app/db.py."""

from pathlib import Path

from app.db import create_db_engine, database_url


def test_pragmas_set_on_live_connection(tmp_path: Path) -> None:
    """All four pragmas are in force on a real connection, not just configured."""
    engine = create_db_engine(database_url(tmp_path / "test.db"))

    try:
        with engine.connect() as connection:
            assert connection.exec_driver_sql("PRAGMA journal_mode").scalar() == "wal"
            assert connection.exec_driver_sql("PRAGMA busy_timeout").scalar() == 5000
            assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
            # 1 is NORMAL.
            assert connection.exec_driver_sql("PRAGMA synchronous").scalar() == 1
    finally:
        engine.dispose()
