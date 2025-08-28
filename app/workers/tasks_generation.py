from celery import shared_task
import uuid
from sqlalchemy.orm import Session

from app.dependencies import SessionLocal
from app.services.ai_provider import get_ai_provider
from app.services.generation_service import store_generated_asset, update_job_status
from app.models.generation_job import JobStatus
from app.models.asset_format import AssetFormat


@shared_task(name="workers.tasks_generation.process_generation_job")
def process_generation_job(job_id: str, project_id: str, asset_ids: list[str], format_ids: list[str]) -> None:
    db: Session = SessionLocal()
    try:
        provider = get_ai_provider()
        update_job_status(db, uuid.UUID(job_id), JobStatus.processing, progress=10)

        # Preload formats to get target dimensions and ensure they exist
        format_uuid_list = [uuid.UUID(fid) for fid in format_ids]
        formats = (
            db.query(AssetFormat)
            .filter(AssetFormat.id.in_(format_uuid_list))
            .all()
        )
        format_map = {str(f.id): f for f in formats}

        progress = 10
        total_steps = max(1, len(asset_ids) * max(1, len(format_ids)))
        step_inc = max(1, int(90 / total_steps))

        for asset_id in asset_ids:
            analysis = provider.analyze_image(f"/data/uploads/{asset_id}.png")
            for fid in format_ids:
                fmt = format_map.get(fid)
                if not fmt:
                    continue  # skip unknown format ids silently

                gen = provider.generate_asset(
                    {
                        "analysis": analysis,
                        "target": {"width": fmt.width, "height": fmt.height},
                        "formatId": fid,
                        "projectId": project_id,
                        "assetId": asset_id,
                    }
                )

                store_generated_asset(
                    db,
                    job_id=uuid.UUID(job_id),
                    original_asset_id=uuid.UUID(asset_id),
                    asset_format_id=uuid.UUID(fid),
                    storage_path=gen.get("url", f"/data/generated/{asset_id}_{fid}.png"),
                    file_type="png",
                    dimensions={"width": fmt.width, "height": fmt.height},
                    is_nsfw=gen.get("isNsfw", False),
                )

                progress = min(100, progress + step_inc)
                update_job_status(db, uuid.UUID(job_id), JobStatus.processing, progress=progress)

        update_job_status(db, uuid.UUID(job_id), JobStatus.completed, progress=100)
    except Exception:
        update_job_status(db, uuid.UUID(job_id), JobStatus.failed, progress=0)
    finally:
        db.close()
