from uuid import UUID
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class FarmCreate(BaseModel):
    name: str
    code: str
    location_id: Optional[UUID] = None
    company_id: UUID
    farm_type: str = "LIVESTOCK"
    description: Optional[str] = None


class FarmRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    code: str
    company_id: UUID
    farm_type: str
    is_active: bool


class LivestockBatchCreate(BaseModel):
    farm_id: UUID
    species: str
    breed: Optional[str] = None
    batch_number: str
    start_date: date
    initial_count: int
    company_id: UUID


class LivestockBatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    farm_id: UUID
    species: str
    batch_number: str
    start_date: date
    initial_count: int
    current_count: int
    status: str
    company_id: UUID


class FeedRecordCreate(BaseModel):
    batch_id: UUID
    farm_id: UUID
    feed_date: date
    feed_type: str
    quantity_kg: Decimal
    unit_cost: Decimal = Decimal("0")
    company_id: UUID


class FeedRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    batch_id: UUID
    farm_id: UUID
    feed_date: date
    feed_type: str
    quantity_kg: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    company_id: UUID
    created_at: datetime


class ProductionRecordCreate(BaseModel):
    farm_id: UUID
    batch_id: Optional[UUID] = None
    production_date: date
    product_type: str
    quantity: Decimal
    unit: str = "KG"
    unit_price: Decimal = Decimal("0")
    company_id: UUID


class ProductionRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    farm_id: UUID
    production_date: date
    product_type: str
    quantity: Decimal
    unit: str
    total_value: Decimal
    company_id: UUID


class MortalityRecordCreate(BaseModel):
    batch_id: UUID
    record_date: date
    count: int
    cause: Optional[str] = None
    company_id: UUID


class MortalityRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    batch_id: UUID
    record_date: date
    count: int
    cause: Optional[str] = None
    company_id: UUID
    created_at: datetime
