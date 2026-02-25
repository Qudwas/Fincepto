from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ItemCategoryCreate(BaseModel):
    name: str
    code: str
    company_id: UUID


class ItemCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    code: str
    company_id: UUID


class ItemCreate(BaseModel):
    code: str
    name: str
    category_id: Optional[UUID] = None
    unit_of_measure: str = "UNIT"
    costing_method: str = "WEIGHTED_AVG"
    standard_cost: Decimal = Decimal("0")
    reorder_level: Decimal = Decimal("0")
    sale_price: Decimal = Decimal("0")
    company_id: UUID
    is_active: bool = True
    description: Optional[str] = None


class ItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    code: str
    name: str
    category_id: Optional[UUID] = None
    unit_of_measure: str
    costing_method: str
    standard_cost: Decimal
    reorder_level: Decimal
    sale_price: Decimal
    company_id: UUID
    is_active: bool


class WarehouseCreate(BaseModel):
    name: str
    code: str
    location_id: Optional[UUID] = None
    company_id: UUID
    is_active: bool = True


class WarehouseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    code: str
    location_id: Optional[UUID] = None
    company_id: UUID
    is_active: bool


class StockMovementCreate(BaseModel):
    item_id: UUID
    warehouse_id: UUID
    movement_type: str
    quantity: Decimal
    unit_cost: Decimal = Decimal("0")
    reference: Optional[str] = None
    company_id: UUID


class StockMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    item_id: UUID
    warehouse_id: UUID
    movement_type: str
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    reference: Optional[str] = None
    movement_date: datetime
    company_id: UUID


class StockBalanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    item_id: UUID
    warehouse_id: UUID
    quantity_on_hand: Decimal
    average_cost: Decimal
    last_updated: datetime
