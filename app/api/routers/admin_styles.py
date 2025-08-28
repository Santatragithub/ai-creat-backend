from __future__ import annotations

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.models.text_style_set import TextStyleSet
from app.schemas.style import TextStyleSet as TextStyleSetSchema, TextStyleSetUpdate

router = APIRouter(tags=["Admin - Formats & Platforms"])


@router.get("/admin/text-style-sets", response_model=List[TextStyleSetSchema])
def list_text_style_sets(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    return db.query(TextStyleSet).filter(TextStyleSet.is_active.is_(True)).all()


@router.post("/admin/text-style-sets", response_model=TextStyleSetSchema, status_code=status.HTTP_201_CREATED)
def create_text_style_set(
    payload: TextStyleSetUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    new_set = TextStyleSet(name=payload.name, styles=payload.styles)
    db.add(new_set)
    db.commit()
    db.refresh(new_set)
    return new_set


@router.put("/admin/text-style-sets/{setId}", response_model=TextStyleSetSchema)
def update_text_style_set(
    setId: uuid.UUID,
    payload: TextStyleSetUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    ts = db.get(TextStyleSet, setId)
    if not ts:
        raise HTTPException(status_code=404, detail="Text style set not found")
    ts.name = payload.name
    ts.styles = payload.styles
    db.add(ts)
    db.commit()
    db.refresh(ts)
    return ts


@router.delete("/admin/text-style-sets/{setId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_text_style_set(
    setId: uuid.UUID,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    ts = db.get(TextStyleSet, setId)
    if not ts:
        raise HTTPException(status_code=404, detail="Text style set not found")
    db.delete(ts)
    db.commit()
    return None
