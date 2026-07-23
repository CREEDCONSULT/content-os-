from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_user
from app.core.config import Settings, get_settings
from app.db.models import Asset, Brand, RightsStatus
from app.db.session import get_db
from app.schemas.contracts import AssetView
from app.services.assets import store_asset

router = APIRouter(
    prefix="/api/v1/assets",
    tags=["assets"],
    dependencies=[Depends(require_user)],
)


@router.get("", response_model=list[AssetView])
def list_assets(db: Session = Depends(get_db)) -> list[Asset]:
    brand_id = db.scalar(select(Brand.id).where(Brand.is_active.is_(True)))
    if not brand_id:
        return []
    return list(
        db.scalars(
            select(Asset).where(Asset.brand_id == brand_id).order_by(Asset.created_at.desc())
        ).all()
    )


@router.post("", response_model=AssetView, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    file: Annotated[UploadFile, File()],
    rights_status: Annotated[RightsStatus, Form()] = RightsStatus.UNKNOWN,
    rights_notes: Annotated[str | None, Form()] = None,
    tags: Annotated[str, Form()] = "",
    content_item_id: Annotated[str | None, Form()] = None,
    production_plan_id: Annotated[str | None, Form()] = None,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Asset:
    content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    return store_asset(
        db,
        settings,
        filename=file.filename or "asset.bin",
        content=content,
        mime_type=file.content_type or "application/octet-stream",
        rights_status=rights_status,
        rights_notes=rights_notes,
        tags=tags.split(","),
        content_item_id=content_item_id,
        production_plan_id=production_plan_id,
    )
