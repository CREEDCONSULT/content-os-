from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal, require_user
from app.core.config import Settings, get_settings
from app.db.models import AgentRun, ContextPack, SkillDefinition
from app.db.session import get_db
from app.schemas.contracts import (
    AgentRunCreate,
    AgentRunList,
    AgentRunView,
    ContextPackView,
    SkillDefinitionView,
)
from app.services.agent import execute_agent_run

router = APIRouter(
    prefix="/api/v1/agent",
    tags=["agent"],
    dependencies=[Depends(require_user)],
)


@router.get("/skills", response_model=list[SkillDefinitionView])
def list_skills(
    enabled: bool | None = Query(default=True),
    db: Session = Depends(get_db),
) -> list[SkillDefinition]:
    statement = select(SkillDefinition)
    if enabled is not None:
        statement = statement.where(SkillDefinition.enabled.is_(enabled))
    return list(db.scalars(statement.order_by(SkillDefinition.slug)).all())


@router.get("/runs", response_model=AgentRunList)
def list_runs(
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
) -> AgentRunList:
    items = list(
        db.scalars(select(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit)).all()
    )
    total = db.scalar(select(func.count(AgentRun.id))) or 0
    return AgentRunList(items=items, total=total)


@router.post("/runs", response_model=AgentRunView, status_code=status.HTTP_201_CREATED)
def create_run(
    payload: AgentRunCreate,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
    settings: Settings = Depends(get_settings),
) -> AgentRun:
    return execute_agent_run(db, payload, user, settings)


@router.get("/runs/{run_id}", response_model=AgentRunView)
def get_run(run_id: str, db: Session = Depends(get_db)) -> AgentRun:
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent run not found.")
    return run


@router.get("/context-packs/{pack_id}", response_model=ContextPackView)
def get_context_pack(pack_id: str, db: Session = Depends(get_db)) -> ContextPack:
    pack = db.get(ContextPack, pack_id)
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context pack not found.",
        )
    return pack
