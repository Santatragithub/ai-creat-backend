from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.models.project import Project, ProjectStatus
from app.models.asset import Asset
from app.schemas.project import ProjectStatusResponse


def create_project(db: Session, user_id: UUID, name: str, assets: List[Asset]) -> Project:
    project = Project(user_id=user_id, name=name, status=ProjectStatus.uploading)
    db.add(project)
    db.flush()
    for asset in assets:
        asset.project_id = project.id
        db.add(asset)
    db.commit()
    db.refresh(project)
    return project


def get_projects(db: Session, user_id: UUID, limit: int = 10, offset: int = 0) -> List[Project]:
    return (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_project_status(db: Session, project_id: UUID) -> Optional[ProjectStatusResponse]:
    project = db.get(Project, project_id)
    if not project:
        return None
    return ProjectStatusResponse(status=project.status.value, progress=0)
