from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal
from app.db.models import (
    Approval,
    ApprovalStatus,
    AuditEvent,
    Brand,
    BriefStatus,
    ContentBrief,
    ContentItem,
    FactCheck,
    HookOption,
    Idea,
    IdeaStatus,
    PipelineEvent,
    PipelineStatus,
    ReviewStatus,
    RiskLevel,
    Script,
    ScriptStatus,
    ScriptVersion,
)
from app.schemas.contracts import (
    BriefFromIdea,
    ContentBriefView,
    FactCheckCreate,
    FactCheckView,
    HookOptionView,
    ScriptApprovalResult,
    ScriptVersionCreate,
    ScriptVersionView,
    ScriptView,
)

BLOCKED_FINANCIAL_PATTERNS = {
    "guaranteed return": r"\bguaranteed?\s+returns?\b",
    "risk-free return": r"\brisk[- ]free\s+returns?\b",
    "direct buy signal": r"\bbuy\s+(?:this|now|immediately)\b",
    "direct sell signal": r"\bsell\s+(?:this|now|immediately)\b",
    "double your money": r"\bdouble\s+your\s+money\b",
}
FINANCIAL_TERMS = {
    "crypto",
    "stock",
    "etf",
    "market",
    "investment",
    "portfolio",
    "wealth",
    "bitcoin",
}


def _active_brand(db: Session) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    return brand


def create_brief_from_idea(
    db: Session,
    idea: Idea,
    payload: BriefFromIdea,
    user: UserPrincipal,
) -> ContentBrief:
    existing = db.scalar(select(ContentBrief).where(ContentBrief.idea_id == idea.id))
    if existing:
        return existing
    if idea.status in {IdeaStatus.REJECTED, IdeaStatus.ARCHIVED}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Rejected or archived ideas cannot become briefs.",
        )

    brand = _active_brand(db)
    content = db.scalar(select(ContentItem).where(ContentItem.idea_id == idea.id))
    if not content:
        content = ContentItem(
            brand_id=brand.id,
            idea_id=idea.id,
            title=idea.title,
            platform=payload.platform,
            format=payload.format,
            pillar=idea.pillar or "Create",
            series=idea.series,
            audience=idea.audience,
            objective=payload.objective
            or idea.strategic_objective
            or "Create useful, evidence-led content.",
            status=PipelineStatus.BRIEF,
            priority="high" if idea.urgency == "high" else "medium",
            readiness_score=35,
            is_demo=idea.is_demo,
        )
        db.add(content)
        db.flush()
    elif content.status in {PipelineStatus.IDEA, PipelineStatus.RESEARCH}:
        db.add(
            PipelineEvent(
                content_item_id=content.id,
                from_status=content.status.value,
                to_status=PipelineStatus.BRIEF.value,
                actor=user.username,
                reason="Content brief created from source idea.",
            )
        )
        content.status = PipelineStatus.BRIEF

    brief = ContentBrief(
        brand_id=brand.id,
        idea_id=idea.id,
        content_item_id=content.id,
        title=idea.title,
        objective=payload.objective
        or idea.strategic_objective
        or "Build authority through useful, evidence-led content.",
        audience=idea.audience,
        platform=payload.platform,
        format=payload.format,
        pillar=idea.pillar or "Create",
        series=idea.series,
        core_message=idea.raw_input,
        audience_problem=payload.audience_problem
        or "The audience needs a clearer path from possibility to practical action.",
        desired_emotion=payload.desired_emotion,
        desired_action=payload.desired_action,
        proof_points=[],
        benchmark_references=[],
        visual_direction=payload.visual_direction,
        production_constraints=payload.production_constraints,
        duration_seconds=payload.duration_seconds,
        cta=payload.cta,
        success_metric=payload.success_metric,
        evidence_status=ReviewStatus.NEEDS_REVIEW,
        status=BriefStatus.PROOF_NEEDED,
        is_demo=idea.is_demo,
    )
    idea.status = IdeaStatus.CONVERTED_TO_BRIEF
    db.add(brief)
    db.flush()
    db.add(
        AuditEvent(
            brand_id=brand.id,
            event_type="brief.created",
            actor=user.username,
            target_type="content_brief",
            target_id=brief.id,
            summary=f'Content brief created from idea: "{idea.title}"',
            details={"idea_id": idea.id, "content_item_id": content.id},
            is_demo=idea.is_demo,
        )
    )
    db.commit()
    db.refresh(brief)
    return brief


def _score_hook(text: str, index: int, selected: bool) -> dict[str, float]:
    word_count = len(text.split())
    clarity = max(5.0, min(9.8, 10.2 - abs(word_count - 11) * 0.18))
    curiosity = min(9.7, 6.4 + (1.1 if "?" in text else 0) + (index % 3) * 0.45)
    specificity = min(9.6, 6.3 + sum(char.isdigit() for char in text) * 0.5)
    brand_fit = (
        9.1 if any(term in text.lower() for term in ("build", "system", "evidence")) else 8.1
    )
    audience_fit = 8.8
    originality = max(6.5, 9.2 - index * 0.22)
    if selected:
        brand_fit = max(brand_fit, 9.3)
    return {
        "clarity_score": round(clarity, 2),
        "curiosity_score": round(curiosity, 2),
        "specificity_score": round(specificity, 2),
        "brand_fit_score": round(brand_fit, 2),
        "audience_fit_score": round(audience_fit, 2),
        "originality_score": round(originality, 2),
        "total_score": round(
            (clarity + curiosity + specificity + brand_fit + audience_fit + originality) / 6,
            2,
        ),
    }


def _hook_category(text: str) -> str:
    lowered = text.lower()
    if "?" in text:
        return "question"
    if any(char.isdigit() for char in text):
        return "specificity"
    if "how" in lowered:
        return "how-to"
    if "stop" in lowered or "not" in lowered:
        return "contrarian"
    return "declaration"


def add_script_version(
    db: Session,
    script: Script,
    payload: ScriptVersionCreate,
    user: UserPrincipal,
) -> ScriptVersion:
    checksum = hashlib.sha256(
        f"{payload.hook_selected}\n{payload.body_text}\n{payload.cta}".encode()
    ).hexdigest()
    duplicate = db.scalar(
        select(ScriptVersion).where(
            ScriptVersion.script_id == script.id,
            ScriptVersion.checksum_sha256 == checksum,
        )
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This script version already exists.",
        )
    current = (
        db.get(ScriptVersion, script.current_version_id) if script.current_version_id else None
    )
    if current:
        current.is_active = False
    version = ScriptVersion(
        script_id=script.id,
        version_number=script.version_count + 1,
        body_text=payload.body_text,
        hook_selected=payload.hook_selected,
        on_screen_text=payload.on_screen_text,
        b_roll_notes=payload.b_roll_notes,
        camera_notes=payload.camera_notes,
        cta=payload.cta,
        duration_seconds=payload.duration_seconds,
        brand_alignment_score=payload.brand_alignment_score,
        originality_score=payload.originality_score,
        evidence_notes=payload.evidence_notes,
        change_summary=payload.change_summary,
        checksum_sha256=checksum,
        created_by=user.username,
        is_active=True,
    )
    db.add(version)
    db.flush()
    script.current_version_id = version.id
    script.version_count += 1
    script.status = ScriptStatus.DRAFT
    script.fact_check_status = ReviewStatus.NEEDS_REVIEW
    script.approval_status = ApprovalStatus.NOT_REQUIRED

    hooks = list(
        dict.fromkeys(
            [
                payload.hook_selected,
                *payload.hook_variants,
            ]
        )
    )
    for index, text in enumerate(hooks):
        selected = text == payload.hook_selected
        db.add(
            HookOption(
                script_version_id=version.id,
                text=text,
                category=_hook_category(text),
                **_score_hook(text, index, selected),
                is_recommended=selected,
            )
        )
    content = db.get(ContentItem, script.content_item_id)
    if content and content.status in {
        PipelineStatus.IDEA,
        PipelineStatus.RESEARCH,
        PipelineStatus.BRIEF,
    }:
        db.add(
            PipelineEvent(
                content_item_id=content.id,
                from_status=content.status.value,
                to_status=PipelineStatus.SCRIPT.value,
                actor=user.username,
                reason="Script version created.",
            )
        )
        content.status = PipelineStatus.SCRIPT
        content.readiness_score = max(content.readiness_score, 50)
    if content:
        content.approval_status = ApprovalStatus.NOT_REQUIRED
    db.commit()
    db.refresh(version)
    return version


def create_script(
    db: Session,
    brief: ContentBrief,
    payload: ScriptVersionCreate,
    user: UserPrincipal,
) -> Script:
    existing = db.scalar(select(Script).where(Script.content_brief_id == brief.id))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This brief already has a script.",
        )
    script = Script(
        brand_id=brief.brand_id,
        content_brief_id=brief.id,
        content_item_id=brief.content_item_id,
        title=brief.title,
        is_demo=brief.is_demo,
    )
    brief.status = BriefStatus.READY
    db.add(script)
    db.flush()
    add_script_version(db, script, payload, user)
    db.refresh(script)
    return script


def script_view(db: Session, script: Script) -> ScriptView:
    version = (
        db.get(ScriptVersion, script.current_version_id) if script.current_version_id else None
    )
    hooks = (
        list(
            db.scalars(
                select(HookOption)
                .where(HookOption.script_version_id == version.id)
                .order_by(HookOption.total_score.desc())
            ).all()
        )
        if version
        else []
    )
    fact_check = (
        db.scalar(select(FactCheck).where(FactCheck.script_version_id == version.id))
        if version
        else None
    )
    base = {
        "id": script.id,
        "content_brief_id": script.content_brief_id,
        "content_item_id": script.content_item_id,
        "title": script.title,
        "status": script.status,
        "current_version_id": script.current_version_id,
        "version_count": script.version_count,
        "fact_check_status": script.fact_check_status,
        "financial_risk": script.financial_risk,
        "approval_status": script.approval_status,
        "is_demo": script.is_demo,
        "created_at": script.created_at,
        "updated_at": script.updated_at,
        "current_version": ScriptVersionView.model_validate(version) if version else None,
        "hooks": [HookOptionView.model_validate(item) for item in hooks],
        "fact_check": FactCheckView.model_validate(fact_check) if fact_check else None,
    }
    return ScriptView.model_validate(base)


def review_script(
    db: Session,
    script: Script,
    payload: FactCheckCreate,
    user: UserPrincipal,
) -> FactCheck:
    version = (
        db.get(ScriptVersion, script.current_version_id) if script.current_version_id else None
    )
    if not version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A script version is required before fact checking.",
        )
    corpus = f"{version.body_text}\n{payload.verified_text}".lower()
    blocked_claims = [
        label for label, pattern in BLOCKED_FINANCIAL_PATTERNS.items() if re.search(pattern, corpus)
    ]
    financial = any(term in corpus for term in FINANCIAL_TERMS)
    missing_sources = bool(payload.claim_table) and not payload.sources
    review_status = (
        ReviewStatus.BLOCKED
        if blocked_claims or payload.unresolved_claims or missing_sources
        else ReviewStatus.VERIFIED
    )
    existing = db.scalar(select(FactCheck).where(FactCheck.script_version_id == version.id))
    fact_check = existing or FactCheck(
        script_version_id=version.id,
        verified_text=payload.verified_text,
        reviewed_by=user.username,
    )
    fact_check.status = review_status
    fact_check.claim_table = payload.claim_table
    fact_check.sources = payload.sources
    fact_check.unresolved_claims = [
        *payload.unresolved_claims,
        *(["Claims have no sources."] if missing_sources else []),
    ]
    fact_check.verified_text = payload.verified_text
    fact_check.confidence = payload.confidence
    fact_check.financial_classification = (
        "prohibited_signal"
        if blocked_claims
        else "educational_financial_content"
        if financial
        else "not_financial"
    )
    fact_check.blocked_claims = blocked_claims
    fact_check.risk_disclosures = (
        [
            "Educational content only; outcomes are uncertain and risks must be explained.",
            "No recommendation or guaranteed performance is implied.",
        ]
        if financial
        else []
    )
    fact_check.reviewed_by = user.username
    fact_check.reviewed_at = datetime.now(UTC)
    if not existing:
        db.add(fact_check)
    script.fact_check_status = review_status
    brief = db.get(ContentBrief, script.content_brief_id)
    if brief:
        brief.evidence_status = review_status
        brief.status = (
            BriefStatus.READY
            if review_status == ReviewStatus.VERIFIED
            else BriefStatus.PROOF_NEEDED
        )
    script.financial_risk = (
        RiskLevel.HIGH if blocked_claims else RiskLevel.MEDIUM if financial else RiskLevel.LOW
    )
    db.commit()
    db.refresh(fact_check)
    return fact_check


def submit_script_for_approval(
    db: Session,
    script: Script,
    user: UserPrincipal,
) -> ScriptApprovalResult:
    if script.fact_check_status != ReviewStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A verified fact check is required before script approval.",
        )
    pending = db.scalar(
        select(Approval).where(
            Approval.action_type == "script_final_approval",
            Approval.target_type == "script",
            Approval.target_id == script.id,
            Approval.status == ApprovalStatus.PENDING,
        )
    )
    if pending:
        return ScriptApprovalResult(script=script_view(db, script), approval_id=pending.id)

    version = db.get(ScriptVersion, script.current_version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A current script version is required.",
        )
    approval = Approval(
        brand_id=script.brand_id,
        action_type="script_final_approval",
        target_type="script",
        target_id=script.id,
        requested_by=user.username,
        risk_level=(
            RiskLevel.HIGH
            if script.financial_risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}
            else RiskLevel.MEDIUM
        ),
        status=ApprovalStatus.PENDING,
        context={
            "script_version_id": version.id,
            "version_number": version.version_number,
            "fact_check_status": script.fact_check_status.value,
            "financial_risk": script.financial_risk.value,
        },
    )
    db.add(approval)
    db.flush()
    version.approval_id = approval.id
    script.status = ScriptStatus.REVIEW
    script.approval_status = ApprovalStatus.PENDING
    content = db.get(ContentItem, script.content_item_id)
    if content:
        if content.status == PipelineStatus.SCRIPT:
            db.add(
                PipelineEvent(
                    content_item_id=content.id,
                    from_status=content.status.value,
                    to_status=PipelineStatus.REVIEW.value,
                    actor=user.username,
                    reason="Final script submitted for approval.",
                )
            )
            content.status = PipelineStatus.REVIEW
        content.approval_status = ApprovalStatus.PENDING
        content.readiness_score = max(content.readiness_score, 65)
    db.commit()
    db.refresh(script)
    return ScriptApprovalResult(script=script_view(db, script), approval_id=approval.id)


def brief_view(brief: ContentBrief) -> ContentBriefView:
    return ContentBriefView.model_validate(brief)
