import uuid
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.asset_format import AssetFormat, FormatType


def get_formats(db: Session, type_filter: Optional[str] = None, category: Optional[str] = None) -> List[AssetFormat]:
    query = db.query(AssetFormat).filter(AssetFormat.is_active == True)
    if type_filter:
        query = query.filter(AssetFormat.type == FormatType(type_filter))
    if category:
        query = query.filter(AssetFormat.category == category)
    return query.all()


def create_format(
    db: Session,
    name: str,
    type: str,
    width: int,
    height: int,
    platform_id: Optional[uuid.UUID] = None,
    category: Optional[str] = None,
    created_by_admin_id: Optional[uuid.UUID] = None,
) -> AssetFormat:
    asset_format = AssetFormat(
        name=name,
        type=FormatType(type),
        platform_id=platform_id,
        category=category,
        width=width,
        height=height,
        created_by_admin_id=created_by_admin_id,
    )
    db.add(asset_format)
    db.commit()
    db.refresh(asset_format)
    return asset_format


def update_format(db: Session, format_id: uuid.UUID, update_data: dict) -> Optional[AssetFormat]:
    fmt = db.get(AssetFormat, format_id)
    if not fmt:
        return None
    for key, value in update_data.items():
        setattr(fmt, key, value)
    db.add(fmt)
    db.commit()
    db.refresh(fmt)
    return fmt


def delete_format(db: Session, format_id: uuid.UUID) -> bool:
    fmt = db.get(AssetFormat, format_id)
    if not fmt:
        return False
    db.delete(fmt)
    db.commit()
    return True
