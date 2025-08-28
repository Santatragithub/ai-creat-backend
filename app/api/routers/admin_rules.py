from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.models.app_settings import AppSettings
from app.schemas.rules import (
    AdaptationRule,
    AIBehaviorRule,
    UploadModerationRule,
    ManualEditingRule,
)

router = APIRouter(tags=["Admin - Rules & Controls"])

DEFAULT_ADAPTATION = {
    "focalPointLogic": "face-centric",
    "layoutGuidance": {
        "safeZone": {"top": 0.05, "bottom": 0.05, "left": 0.05, "right": 0.05},
        "logoSize": 0.1,
    },
}
DEFAULT_AI_BEHAVIOR = {
    "adaptationStrategy": "crop",
    "imageQuality": "medium",
}
DEFAULT_UPLOAD_MODERATION = {
    "allowedImageTypes": ["jpeg", "png", "psd"],
    "maxFileSizeMb": 20,
    "nsfwAlertsActive": False,
}
DEFAULT_MANUAL_EDITING = {
    "editingEnabled": True,
    "croppingEnabled": True,
    "saturationEnabled": True,
    "addTextOrLogoEnabled": True,
    "allowedLogoSources": {"types": ["jpeg", "png", "psd", "ai"], "maxSizeMb": 5},
}


def get_setting(db: Session, key: str) -> dict | None:
    setting = db.query(AppSettings).filter(AppSettings.rule_key == key).first()
    return setting.rule_value if setting else None


def upsert_setting(db: Session, key: str, value: dict):
    setting = db.query(AppSettings).filter(AppSettings.rule_key == key).first()
    if setting:
        setting.rule_value = value
    else:
        setting = AppSettings(rule_key=key, rule_value=value)
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


@router.get("/admin/rules/adaptation", response_model=AdaptationRule)
def get_adaptation_rules(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    value = get_setting(db, "adaptation") or DEFAULT_ADAPTATION
    return AdaptationRule(**value)


@router.put("/admin/rules/adaptation", response_model=AdaptationRule)
def update_adaptation_rules(
    payload: AdaptationRule,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    upsert_setting(db, "adaptation", payload.dict())
    return payload


@router.get("/admin/rules/ai-behavior", response_model=AIBehaviorRule)
def get_ai_behavior(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    value = get_setting(db, "ai-behavior") or DEFAULT_AI_BEHAVIOR
    return AIBehaviorRule(**value)


@router.put("/admin/rules/ai-behavior", response_model=AIBehaviorRule)
def update_ai_behavior(
    payload: AIBehaviorRule,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    upsert_setting(db, "ai-behavior", payload.dict())
    return payload


@router.get("/admin/rules/upload-moderation", response_model=UploadModerationRule)
def get_upload_moderation(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    value = get_setting(db, "upload-moderation") or DEFAULT_UPLOAD_MODERATION
    return UploadModerationRule(**value)


@router.put("/admin/rules/upload-moderation", response_model=UploadModerationRule)
def update_upload_moderation(
    payload: UploadModerationRule,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    upsert_setting(db, "upload-moderation", payload.dict())
    return payload


@router.get("/admin/rules/manual-editing", response_model=ManualEditingRule)
def get_manual_editing(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    value = get_setting(db, "manual-editing") or DEFAULT_MANUAL_EDITING
    return ManualEditingRule(**value)


@router.put("/admin/rules/manual-editing", response_model=ManualEditingRule)
def update_manual_editing(
    payload: ManualEditingRule,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    upsert_setting(db, "manual-editing", payload.dict())
    return payload
