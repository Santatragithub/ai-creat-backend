import uuid
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.generation_job import GenerationJob, JobStatus
from app.models.generated_asset import GeneratedAsset
from app.schemas.generation import GenerationRequest


def create_generation_job(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> GenerationJob:
    job = GenerationJob(project_id=project_id, user_id=user_id, status=JobStatus.pending, progress=0)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_job_status(db: Session, job_id: uuid.UUID, status: JobStatus, progress: int = 0) -> Optional[GenerationJob]:
    job = db.get(GenerationJob, job_id)
    if not job:
        return None
    job.status = status
    job.progress = progress
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def store_generated_asset(
    db: Session,
    job_id: uuid.UUID,
    original_asset_id: uuid.UUID,
    asset_format_id: Optional[uuid.UUID],
    storage_path: str,
    file_type: str,
    dimensions: dict,
    is_nsfw: bool = False,
    manual_edits: Optional[dict] = None,
) -> GeneratedAsset:
    gen_asset = GeneratedAsset(
        job_id=job_id,
        original_asset_id=original_asset_id,
        asset_format_id=asset_format_id,
        storage_path=storage_path,
        file_type=file_type,
        dimensions=dimensions,
        is_nsfw=is_nsfw,
        manual_edits=manual_edits,
    )
    db.add(gen_asset)
    db.commit()
    db.refresh(gen_asset)
    return gen_asset


def get_generated_assets_by_job(db: Session, job_id: uuid.UUID) -> List[GeneratedAsset]:
    return db.query(GeneratedAsset).filter(GeneratedAsset.job_id == job_id).all()
