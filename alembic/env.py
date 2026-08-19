"""Alembic environment.

The database URL comes from `Settings` unless `alembic.ini` (or a caller, via
`config.set_main_option`) supplies one — tests point this at a temp file.
"""

from logging.config import fileConfig

from alembic import context

from app.config import get_settings
from app.db import create_db_engine, database_url
from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _url() -> str:
    """Resolve the URL to migrate, preferring an explicitly configured one."""
    return config.get_main_option("sqlalchemy.url") or database_url(
        get_settings().database_path
    )


def run_migrations_offline() -> None:
    """Emit migrations as SQL without connecting to a database."""
    context.configure(
        url=_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite's ALTER TABLE cannot drop columns, change types, or add
        # constraints. Batch mode recreates and copies the table instead.
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live connection."""
    connectable = create_db_engine(_url())

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # See the note in run_migrations_offline.
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
