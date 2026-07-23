from __future__ import annotations

import hashlib
import re
import uuid
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import Asset, Brand, ContentItem, ProductionPlan, RightsStatus


def store_asset(
    db: Session,
    settings: Settings,
    *,
    filename: str,
    content: bytes,
    mime_type: str,
    rights_status: RightsStatus,
    rights_notes: str | None,
    tags: list[str],
    content_item_id: str | None,
    production_plan_id: str | None,
) -> Asset:
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded asset is empty.",
        )
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Asset exceeds the {settings.max_upload_mb} MB limit.",
        )
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    if content_item_id and not db.get(ContentItem, content_item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked content item not found.",
        )
    if production_plan_id and not db.get(ProductionPlan, production_plan_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked production plan not found.",
        )
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(filename).name).strip(".-")
    safe_name = safe_name[:180] or "asset.bin"
    checksum = hashlib.sha256(content).hexdigest()
    duplicate = db.scalar(
        select(Asset).where(
            Asset.brand_id == brand.id,
            Asset.checksum_sha256 == checksum,
        )
    )
    storage_key = f"assets/{uuid.uuid4()}-{safe_name}"
    root = Path(settings.object_storage_path).resolve()
    target = (root / storage_key).resolve()
    if root != target and root not in target.parents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid asset storage path.",
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(f"{target.suffix}.upload")
    temporary.write_bytes(content)
    temporary.replace(target)
    media_type = mime_type.split("/", 1)[0] if "/" in mime_type else "document"
    asset = Asset(
        brand_id=brand.id,
        content_item_id=content_item_id,
        production_plan_id=production_plan_id,
        filename=safe_name,
        storage_key=storage_key,
        media_type=media_type,
        mime_type=mime_type or "application/octet-stream",
        size_bytes=len(content),
        checksum_sha256=checksum,
        tags=list(dict.fromkeys(tag.strip() for tag in tags if tag.strip())),
        rights_status=rights_status,
        rights_notes=rights_notes,
        original_preserved=True,
        duplicate_of_id=duplicate.id if duplicate else None,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset
