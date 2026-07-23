from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import require_user
from app.core.pipeline import compact_group
from app.db.models import (
    AgentRun,
    Approval,
    ApprovalStatus,
    AuditEvent,
    Brand,
    ContentItem,
    Idea,
    MetricSnapshot,
    PipelineStatus,
    Task,
)
from app.db.session import get_db
from app.schemas.contracts import (
    AgentStatus,
    DashboardActivity,
    DashboardMetric,
    DashboardSummary,
    DashboardTask,
    DashboardUpcoming,
)

router = APIRouter(
    prefix="/api/v1/dashboard", tags=["dashboard"], dependencies=[Depends(require_user)]
)


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)) -> DashboardSummary:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Active brand missing."
        )

    ideas_count = db.scalar(select(func.count(Idea.id)).where(Idea.brand_id == brand.id)) or 0
    content_items = list(
        db.scalars(select(ContentItem).where(ContentItem.brand_id == brand.id)).all()
    )
    in_production = sum(
        item.status
        in {
            PipelineStatus.READY_TO_SHOOT,
            PipelineStatus.SHOT,
            PipelineStatus.EDITING,
            PipelineStatus.REVIEW_EDIT,
        }
        for item in content_items
    )
    published = sum(item.status == PipelineStatus.PUBLISHED for item in content_items)
    engagement = (
        db.scalar(
            select(func.coalesce(func.sum(MetricSnapshot.engagement), 0)).where(
                MetricSnapshot.brand_id == brand.id
            )
        )
        or 0
    )
    demo_metrics = bool(
        db.scalar(
            select(func.count(MetricSnapshot.id)).where(
                MetricSnapshot.brand_id == brand.id,
                MetricSnapshot.is_demo.is_(True),
            )
        )
    )
    pipeline_counts = Counter(compact_group(item.status) for item in content_items)
    tasks = list(
        db.scalars(
            select(Task)
            .where(Task.brand_id == brand.id, Task.status != "done")
            .order_by(Task.due_at, Task.priority)
            .limit(5)
        ).all()
    )
    activity = list(
        db.scalars(
            select(AuditEvent)
            .where(AuditEvent.brand_id == brand.id)
            .order_by(AuditEvent.created_at.desc())
            .limit(5)
        ).all()
    )
    upcoming = sorted(
        [item for item in content_items if item.due_date],
        key=lambda item: item.due_date,
    )[:5]
    pending_approvals = (
        db.scalar(
            select(func.count(Approval.id)).where(
                Approval.brand_id == brand.id,
                Approval.status == ApprovalStatus.PENDING,
            )
        )
        or 0
    )
    agent_run = db.scalar(
        select(AgentRun)
        .where(AgentRun.brand_id == brand.id)
        .order_by(AgentRun.created_at.desc())
        .limit(1)
    )

    return DashboardSummary(
        greeting_name="Mezie",
        brand_name=brand.name,
        signature_line=brand.signature_line,
        metrics=[
            DashboardMetric(
                label="Ideas", value=ideas_count, delta="workspace total", accent="blue"
            ),
            DashboardMetric(
                label="In production", value=in_production, delta="active work", accent="gold"
            ),
            DashboardMetric(
                label="Published", value=published, delta="recorded output", accent="green"
            ),
            DashboardMetric(
                label="Engagement",
                value=engagement,
                delta="demo seed" if demo_metrics else "recorded",
                accent="purple",
                is_demo=demo_metrics,
            ),
        ],
        pipeline_groups={
            name: pipeline_counts.get(name, 0)
            for name in ("ideation", "scripting", "production", "review", "published")
        },
        today=[
            DashboardTask(
                id=item.id,
                title=item.title,
                due_at=item.due_at,
                priority=item.priority,
                status=item.status,
            )
            for item in tasks
        ],
        recent_activity=[
            DashboardActivity(
                id=item.id,
                event_type=item.event_type,
                summary=item.summary,
                created_at=item.created_at,
                is_demo=item.is_demo,
            )
            for item in activity
        ],
        upcoming_content=[
            DashboardUpcoming(
                id=item.id,
                title=item.title,
                platform=item.platform,
                due_date=item.due_date,
                status=item.status,
            )
            for item in upcoming
        ],
        pending_approvals=pending_approvals,
        agent=AgentStatus(
            status=agent_run.status if agent_run else "idle",
            model_alias=agent_run.model_alias if agent_run else "brand_fast_model",
            current_focus=agent_run.intent if agent_run else "Waiting for the next BrandOS task",
            last_run_at=agent_run.created_at if agent_run else None,
            is_mock=not agent_run or agent_run.model_alias.startswith("mock"),
        ),
    )
