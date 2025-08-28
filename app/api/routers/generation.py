from __future__ import annotations

import uuid
from typing import Dict, List, Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.generation_job import GenerationJob, JobStatus
from app.models.generated_asset import GeneratedAsset
from app.models.asset_format import AssetFormat
from app.schemas.generation import GenerationRequest, GenerationJobStatus
from app.models.user import User
from app.workers.tasks_generation import process_generation_job

router = APIRouter(tags=["Generation"])


class EditPayload(BaseModel):
    edits: dict


class DownloadRequest(BaseModel):
    assetIds: List[uuid.UUID]
    format: Literal["jpeg", "png"]
    quality: Literal["high", "medium", "low"]
    grouping: Literal["individual", "batch", "category"]


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
def start_generation(
    req: GenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = GenerationJob(project_id=req.projectId, user_id=current_user.id, status=JobStatus.pending, progress=0)
    db.add(job)
    db.commit()
    db.refresh(job)

    asset_ids: List[str] = []
    process_generation_job.delay(str(job.id), str(req.projectId), asset_ids, [str(fid) for fid in req.formatIds])

    return {"jobId": str(job.id)}


@router.get("/generate/{jobId}/status", response_model=GenerationJobStatus)
def generation_status(
    jobId: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.get(GenerationJob, jobId)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return GenerationJobStatus(status=job.status.value, progress=job.progress)


@router.get("/generate/{jobId}/results")
def generation_results(
    jobId: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, List[dict]]:
    job = db.get(GenerationJob, jobId)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    assets = db.query(GeneratedAsset).filter(GeneratedAsset.job_id == jobId).all()
    results: Dict[str, List[dict]] = {}
    for ga in assets:
        fmt: AssetFormat | None = db.get(AssetFormat, ga.asset_format_id) if ga.asset_format_id else None
        platform_name = None
        format_name = None
        if fmt:
            format_name = fmt.name
            if fmt.platform_id:
                platform_name = str(fmt.platform_id)
        results.setdefault(platform_name or "Generic", []).append(
            {
                "id": str(ga.id),
                "originalAssetId": str(ga.original_asset_id),
                "filename": ga.storage_path.split("/")[-1],
                "assetUrl": f"http://localhost{ga.storage_path}",
                "platformName": platform_name,
                "formatName": format_name,
                "dimensions": ga.dimensions,
                "isNsfw": ga.is_nsfw,
            }
        )
    return results


@router.get("/generated-assets/{assetId}")
def get_generated_asset(
    assetId: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asset = db.get(GeneratedAsset, assetId)
    if not asset:
        raise HTTPException(status_code=404, detail="Generated asset not found")
    fmt: AssetFormat | None = db.get(AssetFormat, asset.asset_format_id) if asset.asset_format_id else None
    return {
        "id": str(asset.id),
        "originalAssetId": str(asset.original_asset_id),
        "filename": asset.storage_path.split("/")[-1],
        "assetUrl": f"http://localhost{asset.storage_path}",
        "platformName": str(fmt.platform_id) if fmt and fmt.platform_id else None,
        "formatName": fmt.name if fmt else None,
        "dimensions": asset.dimensions,
        "isNsfw": asset.is_nsfw,
    }


@router.put("/generated-assets/{assetId}")
def update_generated_asset(
    assetId: uuid.UUID,
    payload: EditPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asset = db.get(GeneratedAsset, assetId)
    if not asset:
        raise HTTPException(status_code=404, detail="Generated asset not found")
    asset.manual_edits = payload.edits
    db.add(asset)
    db.commit()
    fmt: AssetFormat | None = db.get(AssetFormat, asset.asset_format_id) if asset.asset_format_id else None
    return {
        "id": str(asset.id),
        "originalAssetId": str(asset.original_asset_id),
        "filename": asset.storage_path.split("/")[-1],
        "assetUrl": f"http://localhost{asset.storage_path}",
        "platformName": str(fmt.platform_id) if fmt and fmt.platform_id else None,
        "formatName": fmt.name if fmt else None,
        "dimensions": asset.dimensions,
        "isNsfw": asset.is_nsfw,
    }


@router.post("/download")
def download_assets(
    req: DownloadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {"downloadUrl": "http://localhost/data/downloads/fake.zip"}
