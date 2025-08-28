from __future__ import annotations

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, AnyUrl
from uuid import UUID


class GenerationRequest(BaseModel):
    projectId: UUID
    formatIds: List[UUID]
    customResizes: Optional[List[Dict[str, int]]] = None


class GeneratedAsset(BaseModel):
    id: UUID
    originalAssetId: UUID
    filename: str
    assetUrl: AnyUrl
    platformName: Optional[str] = None
    formatName: str
    dimensions: Dict[str, int]
    isNsfw: bool

    class Config:
        orm_mode = True


class GenerationJobStatus(BaseModel):
    status: str
    progress: Optional[int] = None
