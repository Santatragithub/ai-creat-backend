from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.auth import LoginRequest, TokenResponse, UserPreferencesUpdate
from app.models.user import User
from app.utils.security import verify_password, create_jwt

router = APIRouter(tags=["Authentication"])


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_jwt({"sub": str(user.id), "role": getattr(user.role, "value", user.role)})
    return TokenResponse(accessToken=token)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: User = Depends(get_current_user)):
    return None


@router.put("/users/me/preferences")
def update_preferences(
    prefs: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.preferences.update(prefs.dict(exclude_unset=True))
    db.add(current_user)
    db.commit()
    return {"message": "Preferences updated successfully"}
