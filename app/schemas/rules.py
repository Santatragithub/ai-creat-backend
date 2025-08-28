from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel


class SafeZone(BaseModel):
    top: float
    bottom: float
    left: float
    right: float


class LayoutGuidance(BaseModel):
    safeZone: SafeZone
    logoSize: float


class AdaptationRule(BaseModel):
    focalPointLogic: Literal["face-centric", "product-centric", "face-centric & product-centric", "human-centered"]
    layoutGuidance: Optional[LayoutGuidance] = None


class AIBehaviorRule(BaseModel):
    adaptationStrategy: Literal["crop", "extend-canvas", "add-background"]
    imageQuality: Literal["low", "medium", "high"]


class AllowedLogoSources(BaseModel):
    types: List[Literal["jpeg", "png", "psd", "ai"]]
    maxSizeMb: int


class ManualEditingRule(BaseModel):
    editingEnabled: bool
    croppingEnabled: bool
    saturationEnabled: bool
    addTextOrLogoEnabled: bool
    allowedLogoSources: Optional[AllowedLogoSources] = None
