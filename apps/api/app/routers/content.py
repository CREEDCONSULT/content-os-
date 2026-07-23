from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal, require_user
from app.core.pipeline import compact_group
from app.db.models import ContentItem
from app.db.session import get_db
from app.schemas.contracts import ContentList, ContentTransition, ContentView
from app.services.content import transition_content

router = APIRouter(prefix="/api/v1/content", tags=["content"], dependencies=[Depends(require_user)])


@router.get("", response_model=ContentList)
def list_content(db: Session = Depends(get_db)) -> ContentList:
    items = list(
        db.scalars(select(ContentItem).order_by(ContentItem.due_date, ContentItem.created_at)).all()
    )
    groups = Counter(compact_group(item.status) for item in items)
    return ContentList(
        items=[ContentView.model_validate(item) for item in items],
        total=len(items),
        groups={
            name: groups.get(name, 0)
            for name in ("ideation", "scripting", "production", "review", "published")
        },
    )


@router.get("/{content_id}", response_model=ContentView)
def get_content(content_id: str, db: Session = Depends(get_db)) -> ContentItem:
    item = db.get(ContentItem, content_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found.")
    return item


@router.post("/{content_id}/transition", response_model=ContentView)
def transition(
    content_id: str,
    payload: ContentTransition,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> ContentItem:
    item = db.get(ContentItem, content_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found.")
    return transition_content(db, item, payload.to_status, user.username, payload.reason)
