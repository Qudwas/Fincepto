from uuid import UUID
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ProjectTaskCreate(BaseModel):
    project_id: UUID
    name: str
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    status: str = "TODO"
    due_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = None


class ProjectTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    name: str
    status: str
    due_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Decimal
    assigned_to: Optional[UUID] = None


class TimesheetCreate(BaseModel):
    project_id: UUID
    task_id: Optional[UUID] = None
    employee_id: UUID
    date: date
    hours: Decimal
    description: Optional[str] = None
    is_billable: bool = True
    hourly_rate: Optional[Decimal] = None
    company_id: UUID


class TimesheetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    employee_id: UUID
    date: date
    hours: Decimal
    is_billable: bool
    hourly_rate: Optional[Decimal] = None
    company_id: UUID
    created_at: datetime


class ProjectBillingCreate(BaseModel):
    project_id: UUID
    invoice_id: Optional[UUID] = None
    billing_date: date
    amount: Decimal
    description: Optional[str] = None
    company_id: UUID


class ProjectBillingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    billing_date: date
    amount: Decimal
    description: Optional[str] = None
    company_id: UUID
    created_at: datetime
