from __future__ import annotations

import uuid
import enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.base import Base


class FormatType(enum.Enum):
    resizing = "resizing"
    repurposing = "repurposing"


class AssetFormat(Base):
    __tablename__ = "asset_formats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(Enum(FormatType, name="format_type"), nullable=False)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("repurposing_platforms.id", ondelete="CASCADE"), nullable=True)
    category = Column(String(50), nullable=True)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
