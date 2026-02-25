from uuid import UUID
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    code: str
    name: str
    account_type_id: UUID
    parent_id: Optional[UUID] = None
    company_id: UUID
    currency_id: Optional[UUID] = None
    is_active: bool = True
    is_control_account: bool = False


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    code: str
    name: str
    account_type_id: UUID
    parent_id: Optional[UUID] = None
    company_id: UUID
    is_active: bool
    is_control_account: bool


class FiscalYearCreate(BaseModel):
    company_id: UUID
    name: str
    start_date: date
    end_date: date


class FiscalYearRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    company_id: UUID
    name: str
    start_date: date
    end_date: date
    is_closed: bool


class AccountingPeriodCreate(BaseModel):
    fiscal_year_id: UUID
    company_id: UUID
    name: str
    start_date: date
    end_date: date


class AccountingPeriodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    fiscal_year_id: UUID
    company_id: UUID
    name: str
    start_date: date
    end_date: date
    is_locked: bool


class JournalLineCreate(BaseModel):
    account_id: UUID
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    description: Optional[str] = None
    currency_id: Optional[UUID] = None


class JournalLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    account_id: UUID
    debit: Decimal
    credit: Decimal
    description: Optional[str] = None
    functional_debit: Decimal
    functional_credit: Decimal


class JournalCreate(BaseModel):
    company_id: UUID
    reference: str
    description: Optional[str] = None
    journal_date: date
    currency_id: Optional[UUID] = None
    exchange_rate: Decimal = Decimal("1.0")
    business_line_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    lines: List[JournalLineCreate]


class JournalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    company_id: UUID
    reference: str
    description: Optional[str] = None
    journal_date: date
    exchange_rate: Decimal
    status: str
    is_reversal: bool
    reversed_journal_id: Optional[UUID] = None
    lines: List[JournalLineRead] = []
    created_at: datetime


class TaxCodeCreate(BaseModel):
    code: str
    name: str
    rate: Decimal
    tax_type: str
    company_id: UUID
    is_active: bool = True


class TaxCodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    code: str
    name: str
    rate: Decimal
    tax_type: str
    company_id: UUID
    is_active: bool
