from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.hrm import PayrollRun, PayrollLine, Employee
from fastapi import HTTPException


def calculate_paye(gross: Decimal) -> Decimal:
    annual_gross = gross * 12
    tax = Decimal("0")
    if annual_gross <= Decimal("120000"):
        tax = annual_gross * Decimal("0.07")
    elif annual_gross <= Decimal("240000"):
        tax = Decimal("8400") + (annual_gross - Decimal("120000")) * Decimal("0.11")
    elif annual_gross <= Decimal("480000"):
        tax = Decimal("21600") + (annual_gross - Decimal("240000")) * Decimal("0.15")
    elif annual_gross <= Decimal("720000"):
        tax = Decimal("57600") + (annual_gross - Decimal("480000")) * Decimal("0.19")
    elif annual_gross <= Decimal("1200000"):
        tax = Decimal("103200") + (annual_gross - Decimal("720000")) * Decimal("0.21")
    else:
        tax = Decimal("204000") + (annual_gross - Decimal("1200000")) * Decimal("0.24")
    return (tax / 12).quantize(Decimal("0.01"))


class PayrollService:
    @staticmethod
    def calculate(db: Session, payroll_run_id: UUID) -> PayrollRun:
        run = db.get(PayrollRun, payroll_run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Payroll run not found")
        if run.status != "DRAFT":
            raise HTTPException(status_code=400, detail="Only DRAFT payroll runs can be calculated")

        db.query(PayrollLine).filter(PayrollLine.payroll_run_id == payroll_run_id).delete()

        employees = db.query(Employee).filter(
            Employee.company_id == run.company_id,
            Employee.is_active == True,
            Employee.termination_date == None,
        ).all()

        total_gross = Decimal("0")
        total_deductions = Decimal("0")
        total_net = Decimal("0")

        for emp in employees:
            basic = emp.basic_salary
            allowances = Decimal("0")
            gross = basic + allowances
            paye = calculate_paye(gross)
            pension_emp = (gross * Decimal("0.08")).quantize(Decimal("0.01"))
            pension_employer = (gross * Decimal("0.10")).quantize(Decimal("0.01"))
            other_deductions = Decimal("0")
            net = gross - paye - pension_emp - other_deductions

            line = PayrollLine(
                payroll_run_id=run.id,
                employee_id=emp.id,
                basic_salary=basic,
                allowances=allowances,
                gross_salary=gross,
                paye_tax=paye,
                pension_employee=pension_emp,
                pension_employer=pension_employer,
                other_deductions=other_deductions,
                net_pay=net,
            )
            db.add(line)
            total_gross += gross
            total_deductions += paye + pension_emp + other_deductions
            total_net += net

        run.total_gross = total_gross
        run.total_deductions = total_deductions
        run.total_net = total_net
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def approve(db: Session, payroll_run_id: UUID) -> PayrollRun:
        run = db.get(PayrollRun, payroll_run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Payroll run not found")
        if run.status != "DRAFT":
            raise HTTPException(status_code=400, detail="Only DRAFT runs can be approved")
        run.status = "APPROVED"
        db.commit()
        db.refresh(run)
        return run


payroll_service = PayrollService()
