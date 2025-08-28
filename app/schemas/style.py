from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class TextStyleDefinition(BaseModel):
    fontFamily: str
    fontSize: int
    fontWeight: Optional[str] = None
    color: str


class TextStyleGroup(BaseModel):
    title: TextStyleDefinition
    subtitle: TextStyleDefinition
    content: TextStyleDefinition


class TextStyleSet(BaseModel):
    id: UUID
    name: str
    styles: TextStyleGroup

    class Config:
        orm_mode = True


class TextStyleSetUpdate(BaseModel):
    name: str
    styles: TextStyleGroup
