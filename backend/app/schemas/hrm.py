from uuid import UUID
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class EmployeeCreate(BaseModel):
    employee_number: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    hire_date: date
    department_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    job_title: Optional[str] = None
    employment_type: str = "FULL_TIME"
    basic_salary: Decimal = Decimal("0")
    currency_id: Optional[UUID] = None
    company_id: UUID
    user_id: Optional[UUID] = None


class EmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    employee_number: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    hire_date: date
    department_id: Optional[UUID] = None
    job_title: Optional[str] = None
    employment_type: str
    basic_salary: Decimal
    company_id: UUID
    is_active: bool


class LeaveTypeCreate(BaseModel):
    name: str
    days_per_year: int
    is_paid: bool = True
    company_id: UUID


class LeaveTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    days_per_year: int
    is_paid: bool
    company_id: UUID


class LeaveRequestCreate(BaseModel):
    employee_id: UUID
    leave_type_id: UUID
    start_date: date
    end_date: date
    days_requested: Decimal
    reason: Optional[str] = None
    company_id: UUID


class LeaveRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    employee_id: UUID
    leave_type_id: UUID
    start_date: date
    end_date: date
    days_requested: Decimal
    status: str
    reason: Optional[str] = None
    company_id: UUID
    created_at: datetime


class AttendanceRecordCreate(BaseModel):
    employee_id: UUID
    attendance_date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    hours_worked: Decimal = Decimal("0")
    overtime_hours: Decimal = Decimal("0")
    status: str = "PRESENT"
    company_id: UUID


class AttendanceRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    employee_id: UUID
    attendance_date: date
    hours_worked: Decimal
    overtime_hours: Decimal
    status: str
    company_id: UUID


class PayrollRunCreate(BaseModel):
    company_id: UUID
    period_start: date
    period_end: date
    run_date: date


class PayrollRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    company_id: UUID
    period_start: date
    period_end: date
    run_date: date
    status: str
    total_gross: Decimal
    total_deductions: Decimal
    total_net: Decimal
    created_at: datetime


class PayrollLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    payroll_run_id: UUID
    employee_id: UUID
    basic_salary: Decimal
    allowances: Decimal
    gross_salary: Decimal
    paye_tax: Decimal
    pension_employee: Decimal
    pension_employer: Decimal
    net_pay: Decimal
