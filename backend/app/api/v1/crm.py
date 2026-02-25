from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.crm import Lead, Opportunity, SalesOrder, SalesOrderLine
from app.schemas.crm import LeadCreate, LeadRead, OpportunityCreate, OpportunityRead, SalesOrderCreate, SalesOrderRead
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/leads", response_model=List[LeadRead], dependencies=[Depends(require_permission("CRM_MANAGE"))])
def list_leads(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Lead).filter(Lead.company_id == company_id).order_by(Lead.created_at.desc()).all()


@router.post("/leads", response_model=LeadRead, dependencies=[Depends(require_permission("CRM_MANAGE"))])
def create_lead(body: LeadCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Lead(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Lead", module="CRM", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.put("/leads/{lead_id}", response_model=LeadRead, dependencies=[Depends(require_permission("CRM_MANAGE"))])
def update_lead(lead_id: UUID, body: LeadCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.get(Lead, lead_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Lead not found")
    for k, v in body.model_dump().items():
        if hasattr(obj, k):
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/opportunities", response_model=List[OpportunityRead], dependencies=[Depends(require_permission("CRM_MANAGE"))])
def list_opportunities(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Opportunity).filter(Opportunity.company_id == company_id).order_by(Opportunity.created_at.desc()).all()


@router.post("/opportunities", response_model=OpportunityRead, dependencies=[Depends(require_permission("CRM_MANAGE"))])
def create_opportunity(body: OpportunityCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Opportunity(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Opportunity", module="CRM", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/sales-orders", response_model=List[SalesOrderRead], dependencies=[Depends(require_permission("CRM_MANAGE"))])
def list_sales_orders(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(SalesOrder).filter(SalesOrder.company_id == company_id).order_by(SalesOrder.order_date.desc()).all()


@router.post("/sales-orders", response_model=SalesOrderRead, dependencies=[Depends(require_permission("CRM_MANAGE"))])
def create_sales_order(body: SalesOrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from decimal import Decimal
    data = body.model_dump(exclude={"lines"})
    data["created_by"] = current_user.id
    total = sum(l.line_total for l in body.lines)
    data["total_amount"] = total
    obj = SalesOrder(**data)
    db.add(obj)
    db.flush()
    for ld in body.lines:
        line = SalesOrderLine(sales_order_id=obj.id, **ld.model_dump())
        db.add(line)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="SalesOrder", module="CRM", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj
