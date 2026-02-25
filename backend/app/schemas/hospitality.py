from uuid import UUID
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class RoomTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    base_rate: Decimal
    capacity: int = 2
    company_id: UUID


class RoomTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    base_rate: Decimal
    capacity: int
    company_id: UUID


class RoomCreate(BaseModel):
    room_number: str
    room_type_id: UUID
    floor: Optional[int] = None
    company_id: UUID


class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    room_number: str
    room_type_id: UUID
    floor: Optional[int] = None
    status: str
    company_id: UUID


class ReservationCreate(BaseModel):
    reservation_number: str
    company_id: UUID
    room_id: UUID
    guest_name: str
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None
    check_in_date: date
    check_out_date: date
    rate_per_night: Decimal
    total_amount: Decimal


class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    reservation_number: str
    company_id: UUID
    room_id: UUID
    guest_name: str
    check_in_date: date
    check_out_date: date
    rate_per_night: Decimal
    total_amount: Decimal
    status: str
    created_at: datetime


class POSOutletCreate(BaseModel):
    name: str
    outlet_type: str = "RESTAURANT"
    company_id: UUID
    location_id: Optional[UUID] = None


class POSOutletRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    outlet_type: str
    company_id: UUID
    is_active: bool


class POSSaleLineCreate(BaseModel):
    item_id: Optional[UUID] = None
    description: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal


class POSSaleCreate(BaseModel):
    sale_number: str
    outlet_id: UUID
    customer_name: Optional[str] = None
    payment_method: str = "CASH"
    company_id: UUID
    lines: List[POSSaleLineCreate] = []


class POSSaleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    sale_number: str
    outlet_id: UUID
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    payment_method: str
    status: str
    company_id: UUID
    created_at: datetime
