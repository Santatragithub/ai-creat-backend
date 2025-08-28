from celery import shared_task
from sqlalchemy.orm import Session
import uuid

from app.dependencies import SessionLocal
from app.services.moderation_service import check_file_type, check_file_size, nsfw_check_stub
from app.models.asset import Asset


@shared_task(name="workers.tasks_moderation.validate_upload")
def validate_upload(asset_id: str, allowed_types: list[str], max_size_mb: int) -> bool:
    db: Session = SessionLocal()
    try:
        asset = db.get(Asset, uuid.UUID(asset_id))
        if not asset:
            return False

        if not check_file_type(asset.original_filename, allowed_types):
            return False

        if not check_file_size(asset.file_size_bytes, max_size_mb):
            return False

        nsfw_result = nsfw_check_stub(asset.storage_path)
        if nsfw_result.get("is_nsfw", False):
            return False

        return True
    finally:
        db.close()
