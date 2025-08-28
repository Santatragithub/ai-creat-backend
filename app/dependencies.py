from __future__ import annotations

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.user import User
from app.utils.security import decode_jwt

settings = get_settings()

# SQLAlchemy engine/session (Alembic-friendly: single engine definition)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """DB session dependency (scoped per-request)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Auth dependencies (JWT via Authorization: Bearer <token>)
bearer_scheme = HTTPBearer(auto_error=False)


def _raise_unauthorized() -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _raise_forbidden() -> None:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough privileges",
    )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve current user from JWT; raise 401 if invalid/missing."""
    if credentials is None:
        _raise_unauthorized()

    token = credentials.credentials
    try:
        payload = decode_jwt(token)
    except Exception:
        _raise_unauthorized()

    user_id = payload.get("sub")
    if not user_id:
        _raise_unauthorized()

    user = db.get(User, user_id)
    if user is None:
        _raise_unauthorized()

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Ensure the caller is an admin; raise 403 otherwise."""
    if getattr(user, "role", None) != "admin":
        _raise_forbidden()
    return user
