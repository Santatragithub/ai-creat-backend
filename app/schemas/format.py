from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel
from uuid import UUID


class RepurposingPlatform(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True


class RepurposingPlatformCreate(BaseModel):
    name: str


class RepurposingPlatformUpdate(BaseModel):
    name: str


class AssetFormat(BaseModel):
    id: UUID
    name: str
    type: Literal["resizing", "repurposing"]
    platformId: Optional[UUID] = None
    category: Optional[str] = None
    width: int
    height: int

    class Config:
        orm_mode = True


class AssetFormatUpdate(BaseModel):
    name: str
    type: Literal["resizing", "repurposing"]
    platformId: Optional[UUID] = None
    category: Optional[str] = None
    width: int
    height: int
