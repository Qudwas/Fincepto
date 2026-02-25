from uuid import UUID
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class PriceListCreate(BaseModel):
    name: str
    company_id: UUID
    currency_id: Optional[UUID] = None
    effective_date: date


class PriceListRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    company_id: UUID
    effective_date: date
    is_active: bool


class PurchaseOrderLineCreate(BaseModel):
    item_id: UUID
    description: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal


class PurchaseOrderCreate(BaseModel):
    order_number: str
    company_id: UUID
    supplier_id: UUID
    order_date: date
    expected_delivery: Optional[date] = None
    currency_id: Optional[UUID] = None
    lines: List[PurchaseOrderLineCreate] = []


class PurchaseOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    order_number: str
    company_id: UUID
    supplier_id: UUID
    order_date: date
    status: str
    total_amount: Decimal
    created_at: datetime


class GoodsReceiptLineCreate(BaseModel):
    item_id: UUID
    quantity: Decimal
    unit_cost: Decimal
    line_total: Decimal


class GoodsReceiptCreate(BaseModel):
    receipt_number: str
    purchase_order_id: Optional[UUID] = None
    supplier_id: UUID
    company_id: UUID
    receipt_date: date
    warehouse_id: UUID
    lines: List[GoodsReceiptLineCreate] = []


class GoodsReceiptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    receipt_number: str
    company_id: UUID
    supplier_id: UUID
    receipt_date: date
    warehouse_id: UUID
    status: str
    created_at: datetime
