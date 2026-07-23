from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal, require_user
from app.db.models import Brand, ProductionChecklistItem, ProductionPlan, Script
from app.db.session import get_db
from app.schemas.contracts import ChecklistToggle, ProductionPlanUpdate, ProductionPlanView
from app.services.planning import (
    create_production_plan,
    production_plan_view,
    toggle_checklist_item,
    update_production_plan,
)

router = APIRouter(
    prefix="/api/v1/production",
    tags=["production"],
    dependencies=[Depends(require_user)],
)


def _active_brand_id(db: Session) -> str:
    brand_id = db.scalar(select(Brand.id).where(Brand.is_active.is_(True)))
    if not brand_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    return brand_id


@router.get("/plans", response_model=list[ProductionPlanView])
def list_plans(db: Session = Depends(get_db)) -> list[ProductionPlanView]:
    plans = list(
        db.scalars(
            select(ProductionPlan)
            .where(ProductionPlan.brand_id == _active_brand_id(db))
            .order_by(ProductionPlan.updated_at.desc())
        ).all()
    )
    return [production_plan_view(db, plan) for plan in plans]


@router.post(
    "/plans/from-script/{script_id}",
    response_model=ProductionPlanView,
    status_code=status.HTTP_201_CREATED,
)
def plan_from_script(
    script_id: str,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> ProductionPlanView:
    script = db.get(Script, script_id)
    if not script or script.brand_id != _active_brand_id(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found.")
    return production_plan_view(db, create_production_plan(db, script, user))


@router.get("/plans/{plan_id}", response_model=ProductionPlanView)
def get_plan(plan_id: str, db: Session = Depends(get_db)) -> ProductionPlanView:
    plan = db.get(ProductionPlan, plan_id)
    if not plan or plan.brand_id != _active_brand_id(db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production plan not found.",
        )
    return production_plan_view(db, plan)


@router.patch("/plans/{plan_id}", response_model=ProductionPlanView)
def patch_plan(
    plan_id: str,
    payload: ProductionPlanUpdate,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> ProductionPlanView:
    plan = db.get(ProductionPlan, plan_id)
    if not plan or plan.brand_id != _active_brand_id(db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production plan not found.",
        )
    return production_plan_view(db, update_production_plan(db, plan, payload, user))


@router.post("/checklist/{item_id}", response_model=ProductionPlanView)
def set_checklist_item(
    item_id: str,
    payload: ChecklistToggle,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> ProductionPlanView:
    item = db.get(ProductionChecklistItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist item not found.",
        )
    plan = db.get(ProductionPlan, item.production_plan_id)
    if not plan or plan.brand_id != _active_brand_id(db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production plan not found.",
        )
    return production_plan_view(
        db,
        toggle_checklist_item(db, item, payload.is_complete, user),
    )
