from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.hrm import Employee, LeaveType, LeaveRequest, AttendanceRecord, PayrollRun, PayrollLine
from app.schemas.hrm import EmployeeCreate, EmployeeRead, LeaveTypeCreate, LeaveTypeRead, LeaveRequestCreate, LeaveRequestRead, AttendanceRecordCreate, AttendanceRecordRead, PayrollRunCreate, PayrollRunRead, PayrollLineRead
from app.services.audit_service import audit_service
from app.services.payroll_service import payroll_service

router = APIRouter()


@router.get("/employees", response_model=List[EmployeeRead], dependencies=[Depends(require_permission("HR_VIEW"))])
def list_employees(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Employee).filter(Employee.company_id == company_id).all()


@router.post("/employees", response_model=EmployeeRead, dependencies=[Depends(require_permission("HR_VIEW"))])
def create_employee(body: EmployeeCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Employee(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Employee", module="HRM", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/employees/{emp_id}", response_model=EmployeeRead, dependencies=[Depends(require_permission("HR_VIEW"))])
def get_employee(emp_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Employee, emp_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee not found")
    return obj


@router.put("/employees/{emp_id}", response_model=EmployeeRead, dependencies=[Depends(require_permission("HR_VIEW"))])
def update_employee(emp_id: UUID, body: EmployeeCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.get(Employee, emp_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee not found")
    for k, v in body.model_dump().items():
        if hasattr(obj, k):
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/leave-types", response_model=List[LeaveTypeRead], dependencies=[Depends(require_permission("HR_VIEW"))])
def list_leave_types(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(LeaveType).filter(LeaveType.company_id == company_id).all()


@router.post("/leave-types", response_model=LeaveTypeRead, dependencies=[Depends(require_permission("HR_VIEW"))])
def create_leave_type(body: LeaveTypeCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = LeaveType(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/leave-requests", response_model=List[LeaveRequestRead], dependencies=[Depends(require_permission("HR_VIEW"))])
def list_leave_requests(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(LeaveRequest).filter(LeaveRequest.company_id == company_id).order_by(LeaveRequest.created_at.desc()).all()


@router.post("/leave-requests", response_model=LeaveRequestRead, dependencies=[Depends(require_permission("HR_VIEW"))])
def create_leave_request(body: LeaveRequestCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = LeaveRequest(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="LeaveRequest", module="HRM", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.post("/leave-requests/{req_id}/approve", dependencies=[Depends(require_permission("HR_VIEW"))])
def approve_leave(req_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.get(LeaveRequest, req_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Leave request not found")
    obj.status = "APPROVED"
    obj.approver_id = current_user.id
    db.commit()
    audit_service.log(db, action="APPROVE_LEAVE", entity_type="LeaveRequest", module="HRM", user_id=current_user.id, user_email=current_user.email, entity_id=str(req_id))
    return {"message": "Leave approved"}


@router.post("/leave-requests/{req_id}/reject", dependencies=[Depends(require_permission("HR_VIEW"))])
def reject_leave(req_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.get(LeaveRequest, req_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Leave request not found")
    obj.status = "REJECTED"
    obj.approver_id = current_user.id
    db.commit()
    return {"message": "Leave rejected"}


@router.get("/attendance", response_model=List[AttendanceRecordRead], dependencies=[Depends(require_permission("HR_VIEW"))])
def list_attendance(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(AttendanceRecord).filter(AttendanceRecord.company_id == company_id).order_by(AttendanceRecord.attendance_date.desc()).all()


@router.post("/attendance", response_model=AttendanceRecordRead, dependencies=[Depends(require_permission("HR_VIEW"))])
def create_attendance(body: AttendanceRecordCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = AttendanceRecord(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/payroll-runs", response_model=List[PayrollRunRead], dependencies=[Depends(require_permission("PAYROLL_RUN"))])
def list_payroll_runs(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(PayrollRun).filter(PayrollRun.company_id == company_id).order_by(PayrollRun.period_start.desc()).all()


@router.post("/payroll-runs", response_model=PayrollRunRead, dependencies=[Depends(require_permission("PAYROLL_RUN"))])
def create_payroll_run(body: PayrollRunCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = PayrollRun(**body.model_dump(), created_by=current_user.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/payroll-runs/{run_id}/calculate", response_model=PayrollRunRead, dependencies=[Depends(require_permission("PAYROLL_RUN"))])
def calculate_payroll(run_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    run = payroll_service.calculate(db, run_id)
    audit_service.log(db, action="CALCULATE_PAYROLL", entity_type="PayrollRun", module="HRM", user_id=current_user.id, user_email=current_user.email, entity_id=str(run_id))
    return run


@router.post("/payroll-runs/{run_id}/approve", response_model=PayrollRunRead, dependencies=[Depends(require_permission("PAYROLL_RUN"))])
def approve_payroll(run_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    run = payroll_service.approve(db, run_id)
    audit_service.log(db, action="APPROVE_PAYROLL", entity_type="PayrollRun", module="HRM", user_id=current_user.id, user_email=current_user.email, entity_id=str(run_id))
    return run


@router.get("/payroll-runs/{run_id}/lines", response_model=List[PayrollLineRead], dependencies=[Depends(require_permission("PAYROLL_RUN"))])
def get_payroll_lines(run_id: UUID, db: Session = Depends(get_db)):
    return db.query(PayrollLine).filter(PayrollLine.payroll_run_id == run_id).all()
