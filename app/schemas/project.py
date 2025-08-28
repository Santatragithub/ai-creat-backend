from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field, AnyUrl
from datetime import datetime
from uuid import UUID


class FileCounts(BaseModel):
    psd: int = 0
    jpg: int = 0
    png: int = 0


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    status: str
    submitDate: datetime
    fileCounts: FileCounts

    class Config:
        orm_mode = True


class ProjectStatusResponse(BaseModel):
    status: str
    progress: Optional[int] = None


class AssetPreviewMetadata(BaseModel):
    layers: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    dpi: Optional[int] = None
    detectedElements: Optional[List[str]] = None


class AssetPreview(BaseModel):
    id: UUID
    filename: str
    previewUrl: AnyUrl
    metadata: AssetPreviewMetadata

    class Config:
        orm_mode = True
