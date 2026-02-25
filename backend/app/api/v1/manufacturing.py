from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.manufacturing import BillOfMaterials, BOMLine, ProductionOrder, ProductionConsumption
from app.schemas.manufacturing import BOMCreate, BOMRead, ProductionOrderCreate, ProductionOrderRead
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/boms", response_model=List[BOMRead], dependencies=[Depends(require_permission("MANUFACTURING_MANAGE"))])
def list_boms(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(BillOfMaterials).filter(BillOfMaterials.company_id == company_id).all()


@router.post("/boms", response_model=BOMRead, dependencies=[Depends(require_permission("MANUFACTURING_MANAGE"))])
def create_bom(body: BOMCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    data = body.model_dump(exclude={"lines"})
    obj = BillOfMaterials(**data)
    db.add(obj)
    db.flush()
    for ld in body.lines:
        line = BOMLine(bom_id=obj.id, **ld.model_dump())
        db.add(line)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="BOM", module="MANUFACTURING", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/orders", response_model=List[ProductionOrderRead], dependencies=[Depends(require_permission("MANUFACTURING_MANAGE"))])
def list_production_orders(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(ProductionOrder).filter(ProductionOrder.company_id == company_id).order_by(ProductionOrder.created_at.desc()).all()


@router.post("/orders", response_model=ProductionOrderRead, dependencies=[Depends(require_permission("MANUFACTURING_MANAGE"))])
def create_production_order(body: ProductionOrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    data = body.model_dump()
    data["created_by"] = current_user.id
    obj = ProductionOrder(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="ProductionOrder", module="MANUFACTURING", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.post("/orders/{order_id}/start", response_model=ProductionOrderRead, dependencies=[Depends(require_permission("MANUFACTURING_MANAGE"))])
def start_production_order(order_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from datetime import date
    obj = db.get(ProductionOrder, order_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Production order not found")
    obj.status = "IN_PROGRESS"
    obj.actual_start = date.today()
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="START_PRODUCTION", entity_type="ProductionOrder", module="MANUFACTURING", user_id=current_user.id, user_email=current_user.email, entity_id=str(order_id))
    return obj


@router.post("/orders/{order_id}/complete", response_model=ProductionOrderRead, dependencies=[Depends(require_permission("MANUFACTURING_MANAGE"))])
def complete_production_order(order_id: UUID, produced_qty: float, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from datetime import date
    from decimal import Decimal
    obj = db.get(ProductionOrder, order_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Production order not found")
    obj.status = "COMPLETED"
    obj.actual_end = date.today()
    obj.produced_quantity = Decimal(str(produced_qty))
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="COMPLETE_PRODUCTION", entity_type="ProductionOrder", module="MANUFACTURING", user_id=current_user.id, user_email=current_user.email, entity_id=str(order_id))
    return obj
