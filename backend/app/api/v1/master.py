from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.master import Company, Currency, BusinessLine, Location, Department, CostCenter, Project
from app.schemas.master import (
    CompanyCreate, CompanyRead, CurrencyCreate, CurrencyRead,
    BusinessLineCreate, BusinessLineRead, LocationCreate, LocationRead,
    DepartmentCreate, DepartmentRead, CostCenterCreate, CostCenterRead,
    ProjectCreate, ProjectRead,
)
from app.services.audit_service import audit_service

router = APIRouter()


def make_crud_routes(model_cls, schema_create, schema_read, module_name: str, perm: str):
    @router.get(f"/{module_name}", response_model=List[schema_read])
    def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        return db.query(model_cls).offset(skip).limit(limit).all()

    @router.post(f"/{module_name}", response_model=schema_read, dependencies=[Depends(require_permission(perm))])
    def create_item(body: schema_create, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        data = body.model_dump()
        obj = model_cls(**{k: v for k, v in data.items() if hasattr(model_cls, k)})
        db.add(obj)
        db.commit()
        db.refresh(obj)
        audit_service.log(db, action="CREATE", entity_type=model_cls.__name__, module=module_name.upper(), user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
        return obj

    @router.get(f"/{module_name}/{{item_id}}", response_model=schema_read)
    def get_item(item_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        obj = db.get(model_cls, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{module_name} not found")
        return obj

    @router.put(f"/{module_name}/{{item_id}}", response_model=schema_read, dependencies=[Depends(require_permission(perm))])
    def update_item(item_id: UUID, body: schema_create, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        obj = db.get(model_cls, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{module_name} not found")
        for k, v in body.model_dump().items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        audit_service.log(db, action="UPDATE", entity_type=model_cls.__name__, module=module_name.upper(), user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
        return obj

    @router.delete(f"/{module_name}/{{item_id}}", dependencies=[Depends(require_permission(perm))])
    def delete_item(item_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        obj = db.get(model_cls, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{module_name} not found")
        if hasattr(obj, "is_active"):
            obj.is_active = False
            db.commit()
        else:
            db.delete(obj)
            db.commit()
        audit_service.log(db, action="DELETE", entity_type=model_cls.__name__, module=module_name.upper(), user_id=current_user.id, user_email=current_user.email, entity_id=str(item_id))
        return {"message": "Deleted"}


make_crud_routes(Company, CompanyCreate, CompanyRead, "companies", "SYSTEM_ADMIN")
make_crud_routes(Currency, CurrencyCreate, CurrencyRead, "currencies", "SYSTEM_ADMIN")
make_crud_routes(BusinessLine, BusinessLineCreate, BusinessLineRead, "business-lines", "SYSTEM_ADMIN")
make_crud_routes(Location, LocationCreate, LocationRead, "locations", "SYSTEM_ADMIN")
make_crud_routes(Department, DepartmentCreate, DepartmentRead, "departments", "SYSTEM_ADMIN")
make_crud_routes(CostCenter, CostCenterCreate, CostCenterRead, "cost-centers", "SYSTEM_ADMIN")
make_crud_routes(Project, ProjectCreate, ProjectRead, "projects", "PROJECTS_MANAGE")
