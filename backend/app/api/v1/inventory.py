from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.inventory import ItemCategory, Item, Warehouse, StockMovement, StockBalance
from app.schemas.inventory import ItemCategoryCreate, ItemCategoryRead, ItemCreate, ItemRead, WarehouseCreate, WarehouseRead, StockMovementCreate, StockMovementRead, StockBalanceRead
from app.crud.inventory import create_stock_movement, get_stock_on_hand
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/categories", response_model=List[ItemCategoryRead], dependencies=[Depends(require_permission("INVENTORY_MANAGE"))])
def list_categories(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(ItemCategory).filter(ItemCategory.company_id == company_id).all()


@router.post("/categories", response_model=ItemCategoryRead, dependencies=[Depends(require_permission("INVENTORY_MANAGE"))])
def create_category(body: ItemCategoryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = ItemCategory(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="ItemCategory", module="INVENTORY", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/items", response_model=List[ItemRead], dependencies=[Depends(require_permission("INVENTORY_MANAGE"))])
def list_items(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Item).filter(Item.company_id == company_id).order_by(Item.code).all()


@router.post("/items", response_model=ItemRead, dependencies=[Depends(require_permission("INVENTORY_MANAGE"))])
def create_item(body: ItemCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Item(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Item", module="INVENTORY", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/items/{item_id}", response_model=ItemRead, dependencies=[Depends(require_permission("INVENTORY_MANAGE"))])
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Item, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return obj


@router.put("/items/{item_id}", response_model=ItemRead, dependencies=[Depends(require_permission("INVENTORY_MANAGE"))])
def update_item(item_id: UUID, body: ItemCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.get(Item, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    for k, v in body.model_dump().items():
        if hasattr(obj, k):
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/warehouses", response_model=List[WarehouseRead], dependencies=[Depends(require_permission("INVENTORY_MANAGE"))])
def list_warehouses(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Warehouse).filter(Warehouse.company_id == company_id).all()


@router.post("/warehouses", response_model=WarehouseRead, dependencies=[Depends(require_permission("INVENTORY_MANAGE"))])
def create_warehouse(body: WarehouseCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Warehouse(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Warehouse", module="INVENTORY", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.post("/movements", response_model=StockMovementRead, dependencies=[Depends(require_permission("INVENTORY_MANAGE"))])
def create_movement(body: StockMovementCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    mv = create_stock_movement(db, body.item_id, body.warehouse_id, body.movement_type, body.quantity, body.unit_cost, body.reference, body.company_id, current_user.id)
    audit_service.log(db, action="STOCK_MOVEMENT", entity_type="StockMovement", module="INVENTORY", user_id=current_user.id, user_email=current_user.email, entity_id=str(mv.id), after_state={"type": body.movement_type, "qty": float(body.quantity)})
    return mv


@router.get("/stock", response_model=List[StockBalanceRead], dependencies=[Depends(require_permission("INVENTORY_MANAGE"))])
def get_stock(company_id: UUID, warehouse_id: Optional[UUID] = None, item_id: Optional[UUID] = None, db: Session = Depends(get_db)):
    return get_stock_on_hand(db, company_id, warehouse_id, item_id)
