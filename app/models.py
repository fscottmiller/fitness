"""SQLAlchemy declarative base.

Tables are defined in #1; this module exists now so `db.py` and Alembic have a
single `Base.metadata` to point at.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for every ORM model."""
