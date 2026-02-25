from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.budget import Budget, BudgetLine
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetLineRead
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/", response_model=List[BudgetRead], dependencies=[Depends(require_permission("ACCOUNTING_FORECASTS_MANAGE"))])
def list_budgets(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Budget).filter(Budget.company_id == company_id).all()


@router.post("/", response_model=BudgetRead, dependencies=[Depends(require_permission("ACCOUNTING_FORECASTS_MANAGE"))])
def create_budget(body: BudgetCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    data = body.model_dump(exclude={"lines"})
    data["created_by"] = current_user.id
    obj = Budget(**data)
    db.add(obj)
    db.flush()
    for ld in body.lines:
        line = BudgetLine(budget_id=obj.id, **ld.model_dump())
        db.add(line)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Budget", module="BUDGET", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/{budget_id}", response_model=BudgetRead, dependencies=[Depends(require_permission("ACCOUNTING_FORECASTS_MANAGE"))])
def get_budget(budget_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Budget, budget_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Budget not found")
    return obj


@router.get("/{budget_id}/lines", response_model=List[BudgetLineRead], dependencies=[Depends(require_permission("ACCOUNTING_FORECASTS_MANAGE"))])
def get_budget_lines(budget_id: UUID, db: Session = Depends(get_db)):
    return db.query(BudgetLine).filter(BudgetLine.budget_id == budget_id).all()


@router.post("/{budget_id}/approve", dependencies=[Depends(require_permission("ACCOUNTING_FORECASTS_MANAGE"))])
def approve_budget(budget_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.get(Budget, budget_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Budget not found")
    obj.status = "APPROVED"
    db.commit()
    audit_service.log(db, action="APPROVE_BUDGET", entity_type="Budget", module="BUDGET", user_id=current_user.id, user_email=current_user.email, entity_id=str(budget_id))
    return {"message": "Budget approved"}
