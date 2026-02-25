from uuid import UUID
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    code: str
    currency_id: Optional[UUID] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    code: str
    currency_id: Optional[UUID] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    is_active: bool


class CurrencyCreate(BaseModel):
    code: str
    name: str
    symbol: str
    exchange_rate: Decimal = Decimal("1.0")
    is_base: bool = False


class CurrencyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    code: str
    name: str
    symbol: str
    exchange_rate: Decimal
    is_base: bool


class BusinessLineCreate(BaseModel):
    name: str
    code: str
    company_id: Optional[UUID] = None


class BusinessLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    code: str
    company_id: Optional[UUID] = None


class LocationCreate(BaseModel):
    name: str
    code: str
    company_id: UUID


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    code: str
    company_id: UUID


class DepartmentCreate(BaseModel):
    name: str
    code: str
    company_id: UUID


class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    code: str
    company_id: UUID


class CostCenterCreate(BaseModel):
    name: str
    code: str
    company_id: UUID


class CostCenterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    code: str
    company_id: UUID


class ProjectCreate(BaseModel):
    name: str
    code: str
    company_id: UUID
    status: str = "ACTIVE"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    description: Optional[str] = None
    customer_id: Optional[UUID] = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    code: str
    company_id: UUID
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    description: Optional[str] = None
    customer_id: Optional[UUID] = None
