from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal, require_user
from app.db.models import AgentToolCall, ProposedDashboardAction
from app.db.session import get_db
from app.schemas.contracts import (
    AgentToolCallView,
    DashboardActionExecutionResult,
    ProposedDashboardActionCreate,
    ProposedDashboardActionList,
    ProposedDashboardActionView,
)
from app.services.actions import (
    create_dashboard_action,
    execute_dashboard_action,
    list_agent_tool_calls,
    list_dashboard_actions,
)

router = APIRouter(prefix="/api/v1/actions", tags=["actions"], dependencies=[Depends(require_user)])


@router.get("/proposals", response_model=ProposedDashboardActionList)
def list_proposals(
    action_status: str | None = Query(default=None, alias="status", max_length=60),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ProposedDashboardActionList:
    items, total = list_dashboard_actions(
        db,
        status_filter=action_status,
        limit=limit,
        offset=offset,
    )
    return ProposedDashboardActionList(items=items, total=total)


@router.post(
    "/proposals",
    response_model=ProposedDashboardActionView,
    status_code=status.HTTP_201_CREATED,
)
def create_proposal(
    payload: ProposedDashboardActionCreate,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> ProposedDashboardAction:
    return create_dashboard_action(db, payload, user)


@router.post(
    "/proposals/{action_id}/execute",
    response_model=DashboardActionExecutionResult,
)
def execute_proposal(
    action_id: str,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> DashboardActionExecutionResult:
    return execute_dashboard_action(db, action_id, user)


@router.get("/tool-calls", response_model=list[AgentToolCallView])
def list_tool_calls(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[AgentToolCall]:
    return list_agent_tool_calls(db, limit=limit, offset=offset)
