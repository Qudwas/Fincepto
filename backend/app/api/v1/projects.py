from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.projects import ProjectTask, Timesheet, ProjectBilling
from app.schemas.projects import ProjectTaskCreate, ProjectTaskRead, TimesheetCreate, TimesheetRead, ProjectBillingCreate, ProjectBillingRead
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/tasks", response_model=List[ProjectTaskRead], dependencies=[Depends(require_permission("PROJECTS_MANAGE"))])
def list_tasks(project_id: UUID, db: Session = Depends(get_db)):
    return db.query(ProjectTask).filter(ProjectTask.project_id == project_id).all()


@router.post("/tasks", response_model=ProjectTaskRead, dependencies=[Depends(require_permission("PROJECTS_MANAGE"))])
def create_task(body: ProjectTaskCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = ProjectTask(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="ProjectTask", module="PROJECTS", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.put("/tasks/{task_id}", response_model=ProjectTaskRead, dependencies=[Depends(require_permission("PROJECTS_MANAGE"))])
def update_task(task_id: UUID, body: ProjectTaskCreate, db: Session = Depends(get_db)):
    obj = db.get(ProjectTask, task_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Task not found")
    for k, v in body.model_dump().items():
        if hasattr(obj, k):
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/timesheets", response_model=List[TimesheetRead], dependencies=[Depends(require_permission("PROJECTS_MANAGE"))])
def list_timesheets(company_id: UUID, project_id: UUID = None, db: Session = Depends(get_db)):
    q = db.query(Timesheet).filter(Timesheet.company_id == company_id)
    if project_id:
        q = q.filter(Timesheet.project_id == project_id)
    return q.order_by(Timesheet.date.desc()).all()


@router.post("/timesheets", response_model=TimesheetRead, dependencies=[Depends(require_permission("PROJECTS_MANAGE"))])
def create_timesheet(body: TimesheetCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Timesheet(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Timesheet", module="PROJECTS", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/billings", response_model=List[ProjectBillingRead], dependencies=[Depends(require_permission("PROJECTS_MANAGE"))])
def list_billings(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(ProjectBilling).filter(ProjectBilling.company_id == company_id).all()


@router.post("/billings", response_model=ProjectBillingRead, dependencies=[Depends(require_permission("PROJECTS_MANAGE"))])
def create_billing(body: ProjectBillingCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = ProjectBilling(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="ProjectBilling", module="PROJECTS", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj
