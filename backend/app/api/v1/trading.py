from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.trading import PriceList, PurchaseOrder, PurchaseOrderLine, GoodsReceipt, GoodsReceiptLine
from app.schemas.trading import PriceListCreate, PriceListRead, PurchaseOrderCreate, PurchaseOrderRead, GoodsReceiptCreate, GoodsReceiptRead
from app.services.audit_service import audit_service
from app.crud.inventory import create_stock_movement

router = APIRouter()


@router.get("/price-lists", response_model=List[PriceListRead], dependencies=[Depends(require_permission("TRADING_MANAGE"))])
def list_price_lists(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(PriceList).filter(PriceList.company_id == company_id).all()


@router.post("/price-lists", response_model=PriceListRead, dependencies=[Depends(require_permission("TRADING_MANAGE"))])
def create_price_list(body: PriceListCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = PriceList(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/purchase-orders", response_model=List[PurchaseOrderRead], dependencies=[Depends(require_permission("TRADING_MANAGE"))])
def list_purchase_orders(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(PurchaseOrder).filter(PurchaseOrder.company_id == company_id).order_by(PurchaseOrder.order_date.desc()).all()


@router.post("/purchase-orders", response_model=PurchaseOrderRead, dependencies=[Depends(require_permission("TRADING_MANAGE"))])
def create_purchase_order(body: PurchaseOrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from decimal import Decimal
    data = body.model_dump(exclude={"lines"})
    data["created_by"] = current_user.id
    total = sum(l.line_total for l in body.lines)
    data["total_amount"] = total
    obj = PurchaseOrder(**data)
    db.add(obj)
    db.flush()
    for ld in body.lines:
        line = PurchaseOrderLine(purchase_order_id=obj.id, **ld.model_dump())
        db.add(line)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="PurchaseOrder", module="TRADING", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/goods-receipts", response_model=List[GoodsReceiptRead], dependencies=[Depends(require_permission("TRADING_MANAGE"))])
def list_goods_receipts(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(GoodsReceipt).filter(GoodsReceipt.company_id == company_id).order_by(GoodsReceipt.receipt_date.desc()).all()


@router.post("/goods-receipts", response_model=GoodsReceiptRead, dependencies=[Depends(require_permission("TRADING_MANAGE"))])
def create_goods_receipt(body: GoodsReceiptCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from decimal import Decimal
    data = body.model_dump(exclude={"lines"})
    data["created_by"] = current_user.id
    obj = GoodsReceipt(**data)
    db.add(obj)
    db.flush()
    for ld in body.lines:
        line = GoodsReceiptLine(goods_receipt_id=obj.id, **ld.model_dump())
        db.add(line)
        create_stock_movement(db, ld.item_id, body.warehouse_id, "IN", ld.quantity, ld.unit_cost, f"GRN-{obj.receipt_number}", body.company_id, current_user.id)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="GoodsReceipt", module="TRADING", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj
