from __future__ import annotations

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.models.repurposing_platform import RepurposingPlatform
from app.models.asset_format import AssetFormat, FormatType
from app.schemas.format import (
    AssetFormat as AssetFormatSchema,
    AssetFormatUpdate,
    RepurposingPlatform as RepurposingPlatformSchema,
    RepurposingPlatformCreate,
    RepurposingPlatformUpdate,
)

router = APIRouter(tags=["Admin - Formats & Platforms"])


@router.get("/admin/platforms", response_model=List[RepurposingPlatformSchema])
def list_platforms(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    return db.query(RepurposingPlatform).order_by(RepurposingPlatform.name.asc()).all()


@router.post("/admin/platforms", response_model=RepurposingPlatformSchema, status_code=status.HTTP_201_CREATED)
def create_platform(
    payload: RepurposingPlatformCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    platform = RepurposingPlatform(name=payload.name)
    db.add(platform)
    db.commit()
    db.refresh(platform)
    return platform


@router.put("/admin/platforms/{platformId}", response_model=RepurposingPlatformSchema)
def update_platform(
    platformId: uuid.UUID,
    payload: RepurposingPlatformUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    platform = db.get(RepurposingPlatform, platformId)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    platform.name = payload.name
    db.add(platform)
    db.commit()
    db.refresh(platform)
    return platform


@router.delete("/admin/platforms/{platformId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_platform(
    platformId: uuid.UUID,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    platform = db.get(RepurposingPlatform, platformId)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    db.delete(platform)
    db.commit()
    return None


@router.get("/admin/formats", response_model=List[AssetFormatSchema])
def list_formats(
    type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    query = db.query(AssetFormat)
    if type:
        try:
            ft = FormatType(type)
            query = query.filter(AssetFormat.type == ft)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid format type")
    if category:
        query = query.filter(AssetFormat.category == category)
    return query.order_by(AssetFormat.width.asc(), AssetFormat.height.asc()).all()


@router.post("/admin/formats", response_model=AssetFormatSchema, status_code=status.HTTP_201_CREATED)
def create_format(
    payload: AssetFormatUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    fmt = AssetFormat(
        name=payload.name,
        type=FormatType(payload.type),
        platform_id=payload.platformId,
        category=payload.category,
        width=payload.width,
        height=payload.height,
    )
    db.add(fmt)
    db.commit()
    db.refresh(fmt)
    return fmt


@router.put("/admin/formats/{formatId}", response_model=AssetFormatSchema)
def update_format(
    formatId: uuid.UUID,
    payload: AssetFormatUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    fmt = db.get(AssetFormat, formatId)
    if not fmt:
        raise HTTPException(status_code=404, detail="Format not found")
    fmt.name = payload.name
    fmt.type = FormatType(payload.type)
    fmt.platform_id = payload.platformId
    fmt.category = payload.category
    fmt.width = payload.width
    fmt.height = payload.height
    db.add(fmt)
    db.commit()
    db.refresh(fmt)
    return fmt


@router.delete("/admin/formats/{formatId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_format(
    formatId: uuid.UUID,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    fmt = db.get(AssetFormat, formatId)
    if not fmt:
        raise HTTPException(status_code=404, detail="Format not found")
    db.delete(fmt)
    db.commit()
    return None
