from __future__ import annotations

import hashlib
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    BrandDocument,
    BrandDocumentVersion,
    CanonicalStatus,
    ContextPack,
)

MAX_DOCUMENT_CHARS = 4_000
MAX_CONTEXT_CHARS = 12_000


def _terms(value: str) -> set[str]:
    return {
        item
        for item in re.findall(r"[a-z0-9]+", value.lower())
        if len(item) >= 4 and item not in {"with", "from", "that", "this", "into"}
    }


def _score(document: BrandDocument, terms: set[str]) -> tuple[int, str]:
    searchable = " ".join([document.title, document.document_type, *document.tags]).lower()
    score = sum(3 for term in terms if term in searchable)
    if document.document_type == "positioning":
        score += 5
    if document.document_type in {"brand-execution", "product-requirements"}:
        score += 2
    return score, document.title


def build_context_pack(
    db: Session,
    brand_id: str,
    intent: str,
    raw_input: dict[str, object],
) -> ContextPack:
    terms = _terms(f"{intent} {raw_input}")
    documents = list(
        db.scalars(
            select(BrandDocument).where(
                BrandDocument.brand_id == brand_id,
                BrandDocument.canonical_status == CanonicalStatus.CANONICAL,
            )
        ).all()
    )
    ranked = sorted(documents, key=lambda item: _score(item, terms), reverse=True)[:4]
    source_records: list[dict[str, object]] = []
    sections: list[str] = []
    remaining = MAX_CONTEXT_CHARS

    for document in ranked:
        version = db.scalar(
            select(BrandDocumentVersion).where(
                BrandDocumentVersion.brand_document_id == document.id,
                BrandDocumentVersion.is_active.is_(True),
            )
        )
        if not version or remaining <= 0:
            continue
        excerpt = version.content_markdown[: min(MAX_DOCUMENT_CHARS, remaining)]
        remaining -= len(excerpt)
        classification = (
            "approved_strategy"
            if document.document_type in {"positioning", "brand-execution", "brand-record", "skill"}
            else "verified_source_record"
        )
        source_records.append(
            {
                "document_id": document.id,
                "version_id": version.id,
                "title": document.title,
                "source_path": document.source_path,
                "classification": classification,
                "authority": document.canonical_status.value,
                "checksum_sha256": version.checksum_sha256,
            }
        )
        sections.append(
            "\n".join(
                [
                    f"## {document.title}",
                    f"Classification: {classification}",
                    f"Source: {document.source_path}",
                    excerpt,
                ]
            )
        )

    context_markdown = "\n\n".join(sections)
    pack = ContextPack(
        brand_id=brand_id,
        intent=intent,
        source_records=source_records,
        context_markdown=context_markdown,
        token_estimate=max(1, len(context_markdown) // 4),
        freshness_notes=[
            "Canonical source records imported on 2026-07-23.",
            "No external freshness claim is inferred from these internal records.",
        ],
        exclusions=[
            "Draft and archived brand records were excluded.",
            "Sensitive records require an explicit access policy before retrieval.",
        ],
        status="ready" if source_records else "partial",
    )
    db.add(pack)
    db.flush()

    for record in source_records:
        record["pack_fingerprint"] = hashlib.sha256(
            f"{pack.id}:{record['version_id']}".encode()
        ).hexdigest()[:16]
    pack.source_records = source_records
    return pack
