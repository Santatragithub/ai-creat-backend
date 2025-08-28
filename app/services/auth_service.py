from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.utils.security import hash_password, verify_password, create_jwt


def authenticate_user(db: Session, username: str, password: str) -> str:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return create_jwt({"sub": str(user.id), "role": user.role.value})


def create_user(db: Session, username: str, email: str, password: str, role: UserRole = UserRole.user) -> User:
    hashed = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
