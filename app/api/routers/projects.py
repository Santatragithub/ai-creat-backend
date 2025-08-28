from __future__ import annotations

import io
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.project import Project, ProjectStatus
from app.models.asset import Asset
from app.schemas.project import ProjectResponse, ProjectStatusResponse, AssetPreview, AssetPreviewMetadata
from app.utils.file_utils import save_upload_file
from app.utils.image_utils import get_image_dimensions
from app.models.user import User

router = APIRouter(tags=["Projects & Assets"])


@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    results: List[ProjectResponse] = []
    for p in projects:
        counts = {"psd": 0, "jpg": 0, "png": 0}
        assets = db.query(Asset).filter(Asset.project_id == p.id).all()
        for a in assets:
            ext = a.file_type.lower()
            if ext in counts:
                counts[ext] += 1
        results.append(
            ProjectResponse(
                id=p.id,
                name=p.name,
                status=p.status.value,
                submitDate=p.created_at,
                fileCounts=counts,  # matches OpenAPI: psd/jpg/png
            )
        )
    return results


@router.post("/projects/upload", status_code=status.HTTP_202_ACCEPTED)
async def create_project_and_upload(
    projectName: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(user_id=current_user.id, name=projectName, status=ProjectStatus.uploading)
    db.add(project)
    db.commit()
    db.refresh(project)

    for uf in files:
        content = await uf.read()
        path = save_upload_file(io.BytesIO(content), uf.filename)
        dims = {}
        try:
            dims = get_image_dimensions(path)
        except Exception:
            dims = {}

        asset = Asset(
            project_id=project.id,
            original_filename=uf.filename,
            storage_path=path,
            file_type=(uf.filename.split(".")[-1].lower() if "." in uf.filename else "png"),
            file_size_bytes=len(content),
            dimensions=dims or None,
            dpi=None,
            ai_metadata=None,
        )
        db.add(asset)

    project.status = ProjectStatus.ready_for_review
    db.add(project)
    db.commit()

    return {"projectId": str(project.id)}


@router.get("/projects/{projectId}/status", response_model=ProjectStatusResponse)
def project_status(
    projectId: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, projectId)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    progress = 60 if project.status in (ProjectStatus.processing, ProjectStatus.ready_for_review) else 100
    return ProjectStatusResponse(status=project.status.value, progress=progress)


@router.get("/projects/{projectId}/preview", response_model=List[AssetPreview])
def project_preview(
    projectId: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, projectId)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    assets = db.query(Asset).filter(Asset.project_id == project.id).all()
    previews: List[AssetPreview] = []
    for a in assets:
        meta = AssetPreviewMetadata(
            layers=None,
            width=(a.dimensions or {}).get("width"),
            height=(a.dimensions or {}).get("height"),
            dpi=a.dpi,
            detectedElements=(a.ai_metadata or {}).get("detectedElements") if a.ai_metadata else None,
        )
        previews.append(
            AssetPreview(
                id=a.id,
                filename=a.original_filename,
                previewUrl=f"http://localhost{a.storage_path}",
                metadata=meta,
            )
        )
    return previews
