from __future__ import annotations

from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_user
from app.core.config import Settings, get_settings
from app.db.models import DailyBrief, HeartbeatRun
from app.db.session import get_db
from app.schemas.contracts import (
    DailyBriefView,
    HeartbeatRunRequest,
    HeartbeatRunView,
    HeartbeatSettingUpdate,
    HeartbeatSettingView,
)
from app.services.intelligence import (
    get_or_create_heartbeat_setting,
    run_heartbeat,
    update_heartbeat_setting,
)

router = APIRouter(
    prefix="/api/v1/heartbeat",
    tags=["heartbeat"],
    dependencies=[Depends(require_user)],
)


def _view(db: Session, run: HeartbeatRun) -> HeartbeatRunView:
    brief = db.scalar(select(DailyBrief).where(DailyBrief.heartbeat_run_id == run.id))
    payload = {
        **{
            field: getattr(run, field)
            for field in (
                "id",
                "run_date",
                "trigger",
                "idempotency_key",
                "status",
                "source_coverage",
                "model_alias",
                "tools_used",
                "model_cost",
                "tool_cost",
                "context_pack_id",
                "records_changed",
                "errors",
                "confidence",
                "completed_at",
                "is_demo",
                "created_at",
            )
        },
        "brief": DailyBriefView.model_validate(brief) if brief else None,
    }
    return HeartbeatRunView.model_validate(payload)


@router.get("/runs", response_model=list[HeartbeatRunView])
def list_runs(db: Session = Depends(get_db)) -> list[HeartbeatRunView]:
    runs = list(db.scalars(select(HeartbeatRun).order_by(HeartbeatRun.run_date.desc())).all())
    return [_view(db, run) for run in runs]


@router.post("/run", response_model=HeartbeatRunView)
def start_run(
    payload: HeartbeatRunRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> HeartbeatRunView:
    run_date = payload.run_date or datetime.now(UTC).date()
    key = payload.idempotency_key or f"heartbeat:{run_date.isoformat()}"
    run, _, _ = run_heartbeat(
        db,
        settings,
        run_date=run_date,
        trigger="manual",
        idempotency_key=key,
    )
    return _view(db, run)


@router.get("/settings", response_model=HeartbeatSettingView)
def get_setting(db: Session = Depends(get_db)):
    return get_or_create_heartbeat_setting(db)


@router.patch("/settings", response_model=HeartbeatSettingView)
def patch_setting(
    payload: HeartbeatSettingUpdate,
    db: Session = Depends(get_db),
):
    return update_heartbeat_setting(db, payload)


@router.get("/briefs/{brief_date}", response_model=DailyBriefView)
def get_brief(brief_date: date, db: Session = Depends(get_db)):
    brief = db.scalar(select(DailyBrief).where(DailyBrief.brief_date == brief_date))
    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily brief not found.",
        )
    return brief
