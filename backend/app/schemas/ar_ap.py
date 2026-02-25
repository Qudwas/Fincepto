from uuid import UUID
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    code: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    credit_limit: Decimal = Decimal("0")
    currency_id: Optional[UUID] = None
    company_id: UUID
    account_id: Optional[UUID] = None


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    code: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    credit_limit: Decimal
    company_id: UUID
    is_active: bool


class SupplierCreate(BaseModel):
    code: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    currency_id: Optional[UUID] = None
    company_id: UUID
    account_id: Optional[UUID] = None


class SupplierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    code: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company_id: UUID
    is_active: bool


class InvoiceLineCreate(BaseModel):
    item_id: Optional[UUID] = None
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount_rate: Decimal = Decimal("0")
    tax_code_id: Optional[UUID] = None
    line_total: Decimal


class InvoiceCreate(BaseModel):
    invoice_number: str
    invoice_type: str
    party_id: UUID
    party_type: str
    invoice_date: date
    due_date: Optional[date] = None
    currency_id: Optional[UUID] = None
    exchange_rate: Decimal = Decimal("1.0")
    company_id: UUID
    lines: List[InvoiceLineCreate]


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    invoice_number: str
    invoice_type: str
    party_id: UUID
    party_type: str
    invoice_date: date
    due_date: Optional[date] = None
    total_amount: Decimal
    paid_amount: Decimal
    status: str
    company_id: UUID
    created_at: datetime


class PaymentCreate(BaseModel):
    payment_number: str
    payment_type: str
    party_id: UUID
    party_type: str
    payment_date: date
    amount: Decimal
    currency_id: Optional[UUID] = None
    exchange_rate: Decimal = Decimal("1.0")
    account_id: UUID
    company_id: UUID


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    payment_number: str
    payment_type: str
    party_id: UUID
    party_type: str
    payment_date: date
    amount: Decimal
    status: str
    company_id: UUID


class PaymentAllocationCreate(BaseModel):
    payment_id: UUID
    invoice_id: UUID
    allocated_amount: Decimal
