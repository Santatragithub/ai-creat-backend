from __future__ import annotations

from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.dependencies import SessionLocal
from app.models.repurposing_platform import RepurposingPlatform
from app.models.asset_format import AssetFormat, FormatType
from app.models.text_style_set import TextStyleSet
from app.models.app_settings import AppSettings


def upsert_platform(db: Session, name: str) -> RepurposingPlatform:
    obj = db.execute(select(RepurposingPlatform).where(RepurposingPlatform.name == name)).scalar_one_or_none()
    if obj:
        return obj
    obj = RepurposingPlatform(name=name, is_active=True, created_by_admin_id=None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def upsert_format(
    db: Session,
    name: str,
    ftype: FormatType,
    width: int,
    height: int,
    platform_id: UUID | None = None,
    category: str | None = None,
) -> AssetFormat:
    stmt = select(AssetFormat).where(
        AssetFormat.name == name,
        AssetFormat.type == ftype,
        AssetFormat.width == width,
        AssetFormat.height == height,
    )
    if platform_id:
        stmt = stmt.where(AssetFormat.platform_id == platform_id)
    if category:
        stmt = stmt.where(AssetFormat.category == category)

    obj = db.execute(stmt).scalar_one_or_none()
    if obj:
        return obj

    obj = AssetFormat(
        name=name,
        type=ftype,
        platform_id=platform_id,
        category=category,
        width=width,
        height=height,
        is_active=True,
        created_by_admin_id=None,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def upsert_text_style_set(
    db: Session,
    name: str,
    title: dict,
    subtitle: dict,
    content: dict,
) -> TextStyleSet:
    obj = db.execute(select(TextStyleSet).where(TextStyleSet.name == name)).scalar_one_or_none()
    if obj:
        return obj
    styles = {"title": title, "subtitle": subtitle, "content": content}
    obj = TextStyleSet(name=name, styles=styles, is_active=True, created_by_admin_id=None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def upsert_app_setting(db: Session, rule_key: str, rule_value: dict, description: str | None = None) -> AppSettings:
    obj = db.execute(select(AppSettings).where(AppSettings.rule_key == rule_key)).scalar_one_or_none()
    if obj:
        obj.rule_value = rule_value
        if description is not None:
            obj.description = description
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    obj = AppSettings(rule_key=rule_key, rule_value=rule_value, description=description)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def main() -> None:
    db = SessionLocal()
    try:
        instagram = upsert_platform(db, "Instagram")
        facebook = upsert_platform(db, "Facebook")

        upsert_format(db, "Instagram Post", FormatType.repurposing, 1080, 1080, platform_id=instagram.id)
        upsert_format(db, "Instagram Story", FormatType.repurposing, 1080, 1920, platform_id=instagram.id)
        upsert_format(db, "Facebook Post", FormatType.repurposing, 1200, 630, platform_id=facebook.id)

        upsert_format(db, "Hero Banner", FormatType.resizing, 1920, 600, category="Web")
        upsert_format(db, "Mobile Header", FormatType.resizing, 1080, 480, category="Mobile")

        upsert_text_style_set(
            db,
            name="Primary Brand Kit",
            title={"fontFamily": "Inter", "fontSize": 48, "fontWeight": "700", "color": "#111111"},
            subtitle={"fontFamily": "Inter", "fontSize": 28, "fontWeight": "600", "color": "#333333"},
            content={"fontFamily": "Inter", "fontSize": 18, "fontWeight": "400", "color": "#555555"},
        )

        upsert_app_setting(
            db,
            "adaptation",
            {
                "focalPointLogic": "face-centric",
                "layoutGuidance": {"safeZone": {"top": 0.1, "bottom": 0.1, "left": 0.1, "right": 0.1}, "logoSize": 0.08},
            },
            description="Default adaptation rule",
        )
        upsert_app_setting(
            db,
            "ai-behavior",
            {"adaptationStrategy": "crop", "imageQuality": "high"},
            description="Default AI behavior",
        )
        upsert_app_setting(
            db,
            "upload-moderation",
            {"allowedImageTypes": ["jpeg", "png", "psd"], "maxFileSizeMb": 25, "nsfwAlertsActive": True},
            description="Upload and moderation defaults",
        )
        upsert_app_setting(
            db,
            "manual-editing",
            {
                "editingEnabled": True,
                "croppingEnabled": True,
                "saturationEnabled": True,
                "addTextOrLogoEnabled": True,
                "allowedLogoSources": {"types": ["png"], "maxSizeMb": 3},
            },
            description="Manual editing toggles",
        )

        print("Seed completed")
    finally:
        db.close()


if __name__ == "__main__":
    main()
