import uuid
from sqlalchemy.orm import Session
from typing import List

from app.models.asset import Asset


def create_assets(db: Session, project_id: uuid.UUID, files: List[dict]) -> List[Asset]:
    assets: List[Asset] = []
    for f in files:
        asset = Asset(
            project_id=project_id,
            original_filename=f["filename"],
            storage_path=f["path"],
            file_type=f["type"],
            file_size_bytes=f["size"],
            dimensions=f.get("dimensions"),
            dpi=f.get("dpi"),
            ai_metadata=f.get("ai_metadata", {}),
        )
        db.add(asset)
        assets.append(asset)
    db.commit()
    for a in assets:
        db.refresh(a)
    return assets


def get_assets_by_project(db: Session, project_id: uuid.UUID) -> List[Asset]:
    return db.query(Asset).filter(Asset.project_id == project_id).all()
