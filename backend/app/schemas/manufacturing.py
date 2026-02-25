from uuid import UUID
from datetime import date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class BOMLineCreate(BaseModel):
    component_item_id: UUID
    quantity_per_unit: Decimal
    unit_of_measure: str = "UNIT"


class BOMLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    component_item_id: UUID
    quantity_per_unit: Decimal
    unit_of_measure: str


class BOMCreate(BaseModel):
    finished_item_id: UUID
    version: str = "1.0"
    company_id: UUID
    description: Optional[str] = None
    lines: List[BOMLineCreate] = []


class BOMRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    finished_item_id: UUID
    version: str
    is_active: bool
    company_id: UUID
    lines: List[BOMLineRead] = []


class ProductionOrderCreate(BaseModel):
    order_number: str
    company_id: UUID
    finished_item_id: UUID
    bom_id: Optional[UUID] = None
    planned_quantity: Decimal
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    cost_center_id: Optional[UUID] = None


class ProductionOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    order_number: str
    company_id: UUID
    finished_item_id: UUID
    planned_quantity: Decimal
    produced_quantity: Decimal
    scrap_quantity: Decimal
    status: str
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
