from __future__ import annotations

from typing import Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.asset_format import AssetFormat as AssetFormatModel, FormatType
from app.models.user import User
from app.schemas.format import AssetFormat as AssetFormatSchema

router = APIRouter(tags=["User - Formats"])


@router.get(
    "/formats",
    response_model=Dict[str, List[AssetFormatSchema]],
)
def list_formats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resizing = (
        db.query(AssetFormatModel)
        .filter(AssetFormatModel.type == FormatType.resizing, AssetFormatModel.is_active.is_(True))
        .all()
    )
    repurposing = (
        db.query(AssetFormatModel)
        .filter(AssetFormatModel.type == FormatType.repurposing, AssetFormatModel.is_active.is_(True))
        .all()
    )
    return {
        "resizing": [AssetFormatSchema.from_orm(f) for f in resizing],
        "repurposing": [AssetFormatSchema.from_orm(f) for f in repurposing],
    }
