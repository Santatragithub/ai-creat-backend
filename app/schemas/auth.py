from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    accessToken: str


class UserPreferencesUpdate(BaseModel):
    theme: Optional[Literal["light", "dark"]] = None
