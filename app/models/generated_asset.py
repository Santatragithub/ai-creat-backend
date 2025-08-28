from __future__ import annotations

import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.models.base import Base


class GeneratedAsset(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False)  # match SQL schema
    original_asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    asset_format_id = Column(UUID(as_uuid=True), ForeignKey("asset_formats.id", ondelete="SET NULL"), nullable=True)
    storage_path = Column(Text, nullable=False)
    file_type = Column(String(10), nullable=False)
    dimensions = Column(JSONB, nullable=False)
    is_nsfw = Column(Boolean, default=False)
    manual_edits = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
