from __future__ import annotations

import uuid
from sqlalchemy import Column, String, Text, BigInteger, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.models.base import Base


class Asset(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(Text, nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    dimensions = Column(JSONB, nullable=True)  # e.g., {"width": 1920, "height": 1080}
    dpi = Column(Integer, nullable=True)
    ai_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
