from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_user
from app.db.models import Brand, CalendarEvent, CapacityPlan
from app.db.session import get_db
from app.schemas.contracts import (
    CalendarEventCreate,
    CalendarEventView,
    CapacityPlanCreate,
    CapacityPlanView,
)
from app.services.planning import create_calendar_event, upsert_capacity

router = APIRouter(
    prefix="/api/v1/calendar",
    tags=["calendar"],
    dependencies=[Depends(require_user)],
)


def _brand_id(db: Session) -> str:
    brand_id = db.scalar(select(Brand.id).where(Brand.is_active.is_(True)))
    if not brand_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    return brand_id


@router.get("/capacity", response_model=list[CapacityPlanView])
def list_capacity(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[CapacityPlan]:
    query = select(CapacityPlan).where(CapacityPlan.brand_id == _brand_id(db))
    if date_from:
        query = query.where(CapacityPlan.week_start >= date_from)
    if date_to:
        query = query.where(CapacityPlan.week_start <= date_to)
    return list(db.scalars(query.order_by(CapacityPlan.week_start)).all())


@router.put("/capacity", response_model=CapacityPlanView)
def set_capacity(
    payload: CapacityPlanCreate,
    db: Session = Depends(get_db),
) -> CapacityPlan:
    return upsert_capacity(db, payload)


@router.get("/events", response_model=list[CalendarEventView])
def list_events(
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[CalendarEvent]:
    query = select(CalendarEvent).where(CalendarEvent.brand_id == _brand_id(db))
    if date_from:
        query = query.where(CalendarEvent.start_at >= date_from)
    if date_to:
        query = query.where(CalendarEvent.start_at < date_to)
    return list(db.scalars(query.order_by(CalendarEvent.start_at)).all())


@router.post(
    "/events",
    response_model=CalendarEventView,
    status_code=status.HTTP_201_CREATED,
)
def add_event(
    payload: CalendarEventCreate,
    db: Session = Depends(get_db),
) -> CalendarEvent:
    return create_calendar_event(db, payload)
