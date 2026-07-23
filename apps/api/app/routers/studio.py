from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal, require_user
from app.db.models import ContentBrief, FactCheck, Idea, Script, ScriptVersion
from app.db.session import get_db
from app.schemas.contracts import (
    BriefFromIdea,
    ContentBriefView,
    FactCheckCreate,
    FactCheckView,
    ScriptApprovalResult,
    ScriptVersionCreate,
    ScriptVersionView,
    ScriptView,
)
from app.services.studio import (
    add_script_version,
    brief_view,
    create_brief_from_idea,
    create_script,
    review_script,
    script_view,
    submit_script_for_approval,
)

router = APIRouter(
    prefix="/api/v1/studio",
    tags=["studio"],
    dependencies=[Depends(require_user)],
)


@router.get("/briefs", response_model=list[ContentBriefView])
def list_briefs(db: Session = Depends(get_db)) -> list[ContentBrief]:
    return list(db.scalars(select(ContentBrief).order_by(ContentBrief.updated_at.desc())).all())


@router.post(
    "/briefs/from-idea/{idea_id}",
    response_model=ContentBriefView,
    status_code=status.HTTP_201_CREATED,
)
def brief_from_idea(
    idea_id: str,
    payload: BriefFromIdea,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> ContentBrief:
    idea = db.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found.")
    return create_brief_from_idea(db, idea, payload, user)


@router.get("/briefs/{brief_id}", response_model=ContentBriefView)
def get_brief(brief_id: str, db: Session = Depends(get_db)) -> ContentBriefView:
    brief = db.get(ContentBrief, brief_id)
    if not brief:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brief not found.")
    return brief_view(brief)


@router.post(
    "/briefs/{brief_id}/scripts",
    response_model=ScriptView,
    status_code=status.HTTP_201_CREATED,
)
def script_from_brief(
    brief_id: str,
    payload: ScriptVersionCreate,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> ScriptView:
    brief = db.get(ContentBrief, brief_id)
    if not brief:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brief not found.")
    return script_view(db, create_script(db, brief, payload, user))


@router.get("/scripts", response_model=list[ScriptView])
def list_scripts(db: Session = Depends(get_db)) -> list[ScriptView]:
    scripts = list(db.scalars(select(Script).order_by(Script.updated_at.desc())).all())
    return [script_view(db, script) for script in scripts]


@router.get("/scripts/{script_id}", response_model=ScriptView)
def get_script(script_id: str, db: Session = Depends(get_db)) -> ScriptView:
    script = db.get(Script, script_id)
    if not script:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found.")
    return script_view(db, script)


@router.get("/scripts/{script_id}/versions", response_model=list[ScriptVersionView])
def list_script_versions(
    script_id: str,
    db: Session = Depends(get_db),
) -> list[ScriptVersion]:
    if not db.get(Script, script_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found.")
    return list(
        db.scalars(
            select(ScriptVersion)
            .where(ScriptVersion.script_id == script_id)
            .order_by(ScriptVersion.version_number.desc())
        ).all()
    )


@router.post(
    "/scripts/{script_id}/versions",
    response_model=ScriptView,
    status_code=status.HTTP_201_CREATED,
)
def create_script_version(
    script_id: str,
    payload: ScriptVersionCreate,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> ScriptView:
    script = db.get(Script, script_id)
    if not script:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found.")
    add_script_version(db, script, payload, user)
    db.refresh(script)
    return script_view(db, script)


@router.post("/scripts/{script_id}/fact-check", response_model=FactCheckView)
def fact_check_script(
    script_id: str,
    payload: FactCheckCreate,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> FactCheck:
    script = db.get(Script, script_id)
    if not script:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found.")
    return review_script(db, script, payload, user)


@router.post("/scripts/{script_id}/submit", response_model=ScriptApprovalResult)
def submit_script(
    script_id: str,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> ScriptApprovalResult:
    script = db.get(Script, script_id)
    if not script:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found.")
    return submit_script_for_approval(db, script, user)
