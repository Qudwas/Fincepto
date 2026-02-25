from uuid import UUID
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class TravelPackageCreate(BaseModel):
    name: str
    destination: str
    duration_days: int = 1
    base_price: Decimal
    company_id: UUID
    description: Optional[str] = None
    currency_id: Optional[UUID] = None


class TravelPackageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    destination: str
    duration_days: int
    base_price: Decimal
    company_id: UUID
    is_active: bool


class TravelSupplierCreate(BaseModel):
    name: str
    supplier_type: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    company_id: UUID


class TravelSupplierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    supplier_type: str
    company_id: UUID
    is_active: bool


class BookingSupplierCostCreate(BaseModel):
    supplier_id: UUID
    service_description: str
    cost_amount: Decimal
    currency_id: Optional[UUID] = None


class TravelBookingCreate(BaseModel):
    booking_number: str
    company_id: UUID
    package_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    customer_name: str
    customer_email: Optional[str] = None
    travel_date: date
    return_date: Optional[date] = None
    pax_count: int = 1
    total_amount: Decimal
    commission_amount: Decimal = Decimal("0")
    supplier_costs: List[BookingSupplierCostCreate] = []


class TravelBookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    booking_number: str
    company_id: UUID
    customer_name: str
    travel_date: date
    pax_count: int
    total_amount: Decimal
    commission_amount: Decimal
    status: str
    created_at: datetime
