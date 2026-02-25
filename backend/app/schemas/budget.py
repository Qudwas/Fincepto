from uuid import UUID
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class BudgetLineCreate(BaseModel):
    account_id: UUID
    period_date: date
    amount: Decimal
    department_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    project_id: Optional[UUID] = None


class BudgetLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    budget_id: UUID
    account_id: UUID
    period_date: date
    amount: Decimal
    department_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    project_id: Optional[UUID] = None


class BudgetCreate(BaseModel):
    name: str
    company_id: UUID
    fiscal_year_id: UUID
    description: Optional[str] = None
    lines: List[BudgetLineCreate] = []


class BudgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    company_id: UUID
    fiscal_year_id: UUID
    status: str
    description: Optional[str] = None
    created_at: datetime
