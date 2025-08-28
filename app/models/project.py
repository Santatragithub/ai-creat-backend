from __future__ import annotations

import uuid
import enum
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.base import Base


class ProjectStatus(enum.Enum):
    uploading = "uploading"
    processing = "processing"
    ready_for_review = "ready_for_review"
    generating = "generating"
    completed = "completed"
    failed = "failed"


class Project(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Enum(ProjectStatus, name="project_status"), nullable=False, default=ProjectStatus.uploading)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
