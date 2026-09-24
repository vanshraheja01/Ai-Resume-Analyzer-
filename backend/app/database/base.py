from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base — every model inherits from this so
    Base.metadata (used by Alembic autogenerate) sees all tables."""
