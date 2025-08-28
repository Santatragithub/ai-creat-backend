from sqlalchemy.orm import Session
from typing import Optional

from app.models.app_settings import AppSettings


def get_rule(db: Session, rule_key: str) -> Optional[AppSettings]:
    return db.query(AppSettings).filter(AppSettings.rule_key == rule_key).first()


def set_rule(db: Session, rule_key: str, rule_value: dict, description: Optional[str] = None) -> AppSettings:
    rule = db.query(AppSettings).filter(AppSettings.rule_key == rule_key).first()
    if rule:
        rule.rule_value = rule_value
        if description is not None:
            rule.description = description
    else:
        rule = AppSettings(rule_key=rule_key, rule_value=rule_value, description=description)
        db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
