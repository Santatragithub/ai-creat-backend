from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData

# Stable naming convention for Alembic (ensures predictable constraint/index names)
# Ref: https://alembic.sqlalchemy.org/en/latest/naming.html
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata_obj = MetaData(naming_convention=naming_convention)


class Base(DeclarativeBase):
    """Declarative base for all ORM models with sane defaults for Alembic."""
    metadata = metadata_obj

    # Auto-generate __tablename__ as snake_case of class name if not provided
    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[override]
        import re

        name = cls.__name__
        # Convert CamelCase -> snake_case
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        snake = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        return snake
