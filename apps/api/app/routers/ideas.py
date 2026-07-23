from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal, require_user
from app.db.models import AuditEvent, Brand, Idea, IdeaStatus
from app.db.session import get_db
from app.schemas.contracts import IdeaCreate, IdeaList, IdeaScores, IdeaUpdate, IdeaView
from app.services.ideas import apply_scores

router = APIRouter(prefix="/api/v1/ideas", tags=["ideas"], dependencies=[Depends(require_user)])


def active_brand(db: Session) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Active brand missing."
        )
    return brand


@router.get("", response_model=IdeaList)
def list_ideas(
    idea_status: IdeaStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, max_length=200),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> IdeaList:
    statement = select(Idea)
    count_statement = select(func.count(Idea.id))
    if idea_status:
        statement = statement.where(Idea.status == idea_status)
        count_statement = count_statement.where(Idea.status == idea_status)
    if search:
        pattern = f"%{search}%"
        statement = statement.where(Idea.title.ilike(pattern))
        count_statement = count_statement.where(Idea.title.ilike(pattern))
    statement = statement.order_by(Idea.total_priority_score.desc(), Idea.created_at.desc())
    items = list(db.scalars(statement.offset(offset).limit(limit)).all())
    return IdeaList(
        items=[IdeaView.model_validate(item) for item in items],
        total=db.scalar(count_statement) or 0,
    )


@router.post("", response_model=IdeaView, status_code=status.HTTP_201_CREATED)
def create_idea(
    payload: IdeaCreate,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> Idea:
    brand = active_brand(db)
    idea = Idea(brand_id=brand.id, **payload.model_dump(), is_demo=False)
    db.add(idea)
    db.flush()
    db.add(
        AuditEvent(
            brand_id=brand.id,
            event_type="idea.created",
            actor=user.username,
            target_type="idea",
            target_id=idea.id,
            summary=f'Idea captured: "{idea.title}"',
        )
    )
    db.commit()
    db.refresh(idea)
    return idea


@router.get("/{idea_id}", response_model=IdeaView)
def get_idea(idea_id: str, db: Session = Depends(get_db)) -> Idea:
    idea = db.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found.")
    return idea


@router.patch("/{idea_id}", response_model=IdeaView)
def update_idea(idea_id: str, payload: IdeaUpdate, db: Session = Depends(get_db)) -> Idea:
    idea = db.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found.")
    changes = payload.model_dump(exclude_unset=True)
    if changes.get("status") == IdeaStatus.REJECTED and not changes.get("rejection_reason"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Rejected ideas require a rejection reason.",
        )
    for field, value in changes.items():
        setattr(idea, field, value)
    db.commit()
    db.refresh(idea)
    return idea


@router.post("/{idea_id}/score", response_model=IdeaView)
def score_idea(idea_id: str, payload: IdeaScores, db: Session = Depends(get_db)) -> Idea:
    idea = db.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found.")
    apply_scores(idea, payload)
    db.commit()
    db.refresh(idea)
    return idea
