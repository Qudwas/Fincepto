from typing import Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.inventory import StockMovement, StockBalance, Item
from fastapi import HTTPException


def create_stock_movement(
    db: Session,
    item_id: UUID,
    warehouse_id: UUID,
    movement_type: str,
    quantity: Decimal,
    unit_cost: Decimal,
    reference: Optional[str],
    company_id: UUID,
    created_by: Optional[UUID] = None,
) -> StockMovement:
    total_cost = quantity * unit_cost
    movement = StockMovement(
        item_id=item_id,
        warehouse_id=warehouse_id,
        movement_type=movement_type,
        quantity=quantity,
        unit_cost=unit_cost,
        total_cost=total_cost,
        reference=reference,
        company_id=company_id,
        created_by=created_by,
    )
    db.add(movement)

    balance = db.query(StockBalance).filter(
        StockBalance.item_id == item_id,
        StockBalance.warehouse_id == warehouse_id,
    ).first()

    if movement_type in ("IN", "ADJUSTMENT"):
        if balance is None:
            balance = StockBalance(
                item_id=item_id,
                warehouse_id=warehouse_id,
                quantity_on_hand=Decimal("0"),
                average_cost=Decimal("0"),
            )
            db.add(balance)
        if movement_type == "IN":
            old_qty = balance.quantity_on_hand
            old_total = old_qty * balance.average_cost
            new_total = old_total + total_cost
            balance.quantity_on_hand += quantity
            if balance.quantity_on_hand > 0:
                balance.average_cost = new_total / balance.quantity_on_hand
        else:
            balance.quantity_on_hand += quantity
    elif movement_type == "OUT":
        if balance is None or balance.quantity_on_hand < quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        balance.quantity_on_hand -= quantity

    from datetime import datetime
    if balance:
        balance.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(movement)
    return movement


def get_stock_on_hand(db: Session, company_id: UUID, warehouse_id: Optional[UUID] = None, item_id: Optional[UUID] = None):
    query = db.query(StockBalance).join(Item, Item.id == StockBalance.item_id).filter(Item.company_id == company_id)
    if warehouse_id:
        query = query.filter(StockBalance.warehouse_id == warehouse_id)
    if item_id:
        query = query.filter(StockBalance.item_id == item_id)
    return query.all()
