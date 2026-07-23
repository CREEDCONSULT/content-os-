from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_user
from app.db.models import Brand, Experiment
from app.db.session import get_db
from app.schemas.contracts import (
    AnalyticsImportResult,
    AnalyticsOverview,
    ExperimentCreate,
    ExperimentView,
    MetricCreate,
    MetricSnapshotView,
)
from app.services.analytics import (
    analytics_overview,
    create_experiment,
    create_metric,
    import_csv,
)

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["analytics"],
    dependencies=[Depends(require_user)],
)


@router.get("/overview", response_model=AnalyticsOverview)
def overview(db: Session = Depends(get_db)) -> AnalyticsOverview:
    return analytics_overview(db)


@router.post(
    "/metrics",
    response_model=MetricSnapshotView,
    status_code=status.HTTP_201_CREATED,
)
def add_metric(
    payload: MetricCreate,
    db: Session = Depends(get_db),
):
    return create_metric(db, payload)


@router.post("/import", response_model=AnalyticsImportResult)
async def import_metrics(
    file: Annotated[UploadFile, File()],
    db: Session = Depends(get_db),
) -> AnalyticsImportResult:
    return import_csv(db, await file.read(5 * 1024 * 1024 + 1))


@router.get("/experiments", response_model=list[ExperimentView])
def list_experiments(db: Session = Depends(get_db)) -> list[Experiment]:
    brand_id = db.scalar(select(Brand.id).where(Brand.is_active.is_(True)))
    if not brand_id:
        return []
    return list(
        db.scalars(
            select(Experiment)
            .where(Experiment.brand_id == brand_id)
            .order_by(Experiment.updated_at.desc())
        ).all()
    )


@router.post(
    "/experiments",
    response_model=ExperimentView,
    status_code=status.HTTP_201_CREATED,
)
def add_experiment(
    payload: ExperimentCreate,
    db: Session = Depends(get_db),
) -> Experiment:
    return create_experiment(db, payload)
