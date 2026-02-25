from uuid import UUID
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class LeadCreate(BaseModel):
    company_id: UUID
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: str = "NEW"
    assigned_to: Optional[UUID] = None
    notes: Optional[str] = None
    company_name: Optional[str] = None


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    company_id: UUID
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: str
    assigned_to: Optional[UUID] = None
    company_name: Optional[str] = None
    created_at: datetime


class OpportunityCreate(BaseModel):
    company_id: UUID
    lead_id: Optional[UUID] = None
    name: str
    customer_id: Optional[UUID] = None
    stage: str = "PROSPECTING"
    value: Decimal = Decimal("0")
    probability: int = 50
    expected_close_date: Optional[date] = None
    assigned_to: Optional[UUID] = None
    notes: Optional[str] = None
    currency_id: Optional[UUID] = None


class OpportunityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    company_id: UUID
    name: str
    stage: str
    value: Decimal
    probability: int
    expected_close_date: Optional[date] = None
    assigned_to: Optional[UUID] = None
    created_at: datetime


class SalesOrderLineCreate(BaseModel):
    item_id: Optional[UUID] = None
    description: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal


class SalesOrderCreate(BaseModel):
    order_number: str
    company_id: UUID
    customer_id: UUID
    opportunity_id: Optional[UUID] = None
    order_date: date
    status: str = "DRAFT"
    currency_id: Optional[UUID] = None
    lines: List[SalesOrderLineCreate] = []


class SalesOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    order_number: str
    company_id: UUID
    customer_id: UUID
    order_date: date
    status: str
    total_amount: Decimal
    created_at: datetime
