from __future__ import annotations

import csv
import io
from collections import defaultdict
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Brand,
    ContentItem,
    Experiment,
    Insight,
    MetricSnapshot,
)
from app.schemas.contracts import (
    AnalyticsImportResult,
    AnalyticsOverview,
    ExperimentCreate,
    InsightView,
    MetricCreate,
    MetricSnapshotView,
)

CSV_COLUMNS = {
    "platform",
    "views",
    "impressions",
    "engagement",
    "saves",
    "shares",
}


def _brand(db: Session) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    return brand


def create_metric(db: Session, payload: MetricCreate) -> MetricSnapshot:
    brand = _brand(db)
    if payload.content_item_id:
        content = db.get(ContentItem, payload.content_item_id)
        if not content or content.brand_id != brand.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content item not found.",
            )
    metric = MetricSnapshot(
        brand_id=brand.id,
        **payload.model_dump(exclude={"captured_at"}),
        captured_at=payload.captured_at or datetime.now(UTC),
        is_demo=False,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def _integer(row: dict[str, str], name: str, row_number: int) -> int:
    try:
        value = int(row.get(name, "0") or 0)
    except ValueError as exc:
        raise ValueError(f"row {row_number}: {name} must be an integer") from exc
    if value < 0:
        raise ValueError(f"row {row_number}: {name} cannot be negative")
    return value


def import_csv(db: Session, content: bytes) -> AnalyticsImportResult:
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Analytics CSV exceeds the 5 MB import limit.",
        )
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Analytics CSV must be UTF-8 encoded.",
        ) from exc
    reader = csv.DictReader(io.StringIO(decoded))
    columns = set(reader.fieldnames or [])
    missing = sorted(CSV_COLUMNS - columns)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Analytics CSV is missing required columns: {', '.join(missing)}.",
        )
    brand = _brand(db)
    imported = rejected = 0
    errors: list[str] = []
    imported_metrics: list[MetricSnapshot] = []
    for row_number, row in enumerate(reader, 2):
        try:
            platform = (row.get("platform") or "").strip()
            if not platform:
                raise ValueError(f"row {row_number}: platform is required")
            content_item_id = (row.get("content_item_id") or "").strip() or None
            if content_item_id:
                linked = db.get(ContentItem, content_item_id)
                if not linked or linked.brand_id != brand.id:
                    raise ValueError(f"row {row_number}: content_item_id was not found")
            captured_raw = (row.get("captured_at") or "").strip()
            captured_at = (
                datetime.fromisoformat(captured_raw.replace("Z", "+00:00"))
                if captured_raw
                else datetime.now(UTC)
            )
            metric = MetricSnapshot(
                brand_id=brand.id,
                content_item_id=content_item_id,
                platform=platform,
                captured_at=captured_at,
                views=_integer(row, "views", row_number),
                impressions=_integer(row, "impressions", row_number),
                engagement=_integer(row, "engagement", row_number),
                saves=_integer(row, "saves", row_number),
                shares=_integer(row, "shares", row_number),
                watch_time_seconds=float(row.get("watch_time_seconds", "0") or 0),
                is_demo=False,
            )
            if metric.watch_time_seconds < 0:
                raise ValueError(f"row {row_number}: watch_time_seconds cannot be negative")
            db.add(metric)
            db.flush()
            imported_metrics.append(metric)
            imported += 1
        except (ValueError, TypeError) as exc:
            rejected += 1
            errors.append(str(exc))
    insight_ids: list[str] = []
    if imported_metrics:
        views = sum(item.views for item in imported_metrics)
        engagement = sum(item.engagement for item in imported_metrics)
        rate = engagement / views if views else 0
        insight = Insight(
            brand_id=brand.id,
            classification="raw_observation",
            title=f"Imported {imported} performance snapshot{'s' if imported != 1 else ''}",
            observation=(
                f"The imported batch contains {views:,} views and {engagement:,} "
                f"engagement actions ({rate:.2%} of views)."
            ),
            hypothesis=(
                "Format, hook, audience, or distribution may explain differences; "
                "the import alone does not establish causation."
            ),
            evidence=[
                {
                    "metric_snapshot_id": metric.id,
                    "platform": metric.platform,
                    "classification": "verified_import",
                }
                for metric in imported_metrics
            ],
            confidence=0.5,
            status="working",
            is_demo=False,
        )
        db.add(insight)
        db.flush()
        insight_ids.append(insight.id)
    db.commit()
    return AnalyticsImportResult(
        imported=imported,
        rejected=rejected,
        errors=errors[:100],
        insight_ids=insight_ids,
    )


def analytics_overview(db: Session) -> AnalyticsOverview:
    brand = _brand(db)
    metrics = list(
        db.scalars(
            select(MetricSnapshot)
            .where(MetricSnapshot.brand_id == brand.id)
            .order_by(MetricSnapshot.captured_at.desc())
            .limit(200)
        ).all()
    )
    insights = list(
        db.scalars(
            select(Insight)
            .where(Insight.brand_id == brand.id)
            .order_by(Insight.updated_at.desc())
            .limit(50)
        ).all()
    )
    totals = {
        "views": float(sum(item.views for item in metrics)),
        "impressions": float(sum(item.impressions for item in metrics)),
        "engagement": float(sum(item.engagement for item in metrics)),
        "saves": float(sum(item.saves for item in metrics)),
        "shares": float(sum(item.shares for item in metrics)),
    }
    groups: dict[str, dict[str, float]] = defaultdict(
        lambda: {"views": 0, "engagement": 0, "saves": 0, "shares": 0, "records": 0}
    )
    for item in metrics:
        group = groups[item.platform]
        group["views"] += item.views
        group["engagement"] += item.engagement
        group["saves"] += item.saves
        group["shares"] += item.shares
        group["records"] += 1
    breakdown = [
        {"platform": platform, **values}
        for platform, values in sorted(groups.items(), key=lambda pair: -pair[1]["views"])
    ]
    return AnalyticsOverview(
        metrics=[MetricSnapshotView.model_validate(item) for item in metrics],
        insights=[InsightView.model_validate(item) for item in insights],
        totals=totals,
        platform_breakdown=breakdown,
    )


def create_experiment(db: Session, payload: ExperimentCreate) -> Experiment:
    brand = _brand(db)
    if (
        payload.measurement_start
        and payload.measurement_end
        and payload.measurement_end < payload.measurement_start
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Experiment measurement end must not precede its start.",
        )
    normalized_controls = list(
        dict.fromkeys(item.strip() for item in payload.control_conditions if item.strip())
    )
    if not normalized_controls:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one control condition is required.",
        )
    experiment = Experiment(
        brand_id=brand.id,
        **payload.model_dump(exclude={"control_conditions"}),
        control_conditions=normalized_controls,
        status="planned",
        is_demo=False,
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment
