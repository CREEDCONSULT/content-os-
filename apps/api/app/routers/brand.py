from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal, require_user
from app.db.models import BrandDocument, BrandDocumentVersion, CanonicalStatus
from app.db.session import get_db
from app.schemas.contracts import (
    BrandDocumentDetail,
    BrandDocumentSummary,
    BrandDocumentVersionView,
    CreateDocumentVersion,
    VersionCreationResult,
)
from app.services.brand import active_version, create_version

router = APIRouter(prefix="/api/v1/brand", tags=["brand"], dependencies=[Depends(require_user)])


@router.get("/documents", response_model=list[BrandDocumentSummary])
def list_documents(
    canonical_status: CanonicalStatus | None = None,
    search: str | None = Query(default=None, max_length=200),
    db: Session = Depends(get_db),
) -> list[BrandDocument]:
    statement = select(BrandDocument).order_by(BrandDocument.document_type, BrandDocument.title)
    if canonical_status:
        statement = statement.where(BrandDocument.canonical_status == canonical_status)
    if search:
        statement = statement.where(BrandDocument.title.ilike(f"%{search}%"))
    return list(db.scalars(statement).all())


@router.get("/documents/{document_id}", response_model=BrandDocumentDetail)
def get_document(document_id: str, db: Session = Depends(get_db)) -> BrandDocumentDetail:
    document = db.get(BrandDocument, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    summary = BrandDocumentSummary.model_validate(document).model_dump()
    version = active_version(db, document)
    return BrandDocumentDetail(
        **summary,
        current_version=BrandDocumentVersionView.model_validate(version) if version else None,
    )


@router.get(
    "/documents/{document_id}/versions",
    response_model=list[BrandDocumentVersionView],
)
def list_versions(document_id: str, db: Session = Depends(get_db)) -> list[BrandDocumentVersion]:
    if not db.get(BrandDocument, document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    statement = (
        select(BrandDocumentVersion)
        .where(BrandDocumentVersion.brand_document_id == document_id)
        .order_by(BrandDocumentVersion.version_number.desc())
    )
    return list(db.scalars(statement).all())


@router.post(
    "/documents/{document_id}/versions",
    response_model=VersionCreationResult,
    status_code=status.HTTP_201_CREATED,
)
def add_version(
    document_id: str,
    payload: CreateDocumentVersion,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> VersionCreationResult:
    document = db.get(BrandDocument, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    version, approval, activated = create_version(
        db,
        document,
        payload.content_markdown,
        payload.change_summary,
        user.username,
    )
    return VersionCreationResult(
        version=BrandDocumentVersionView.model_validate(version),
        approval_id=approval.id if approval else None,
        activated=activated,
    )
