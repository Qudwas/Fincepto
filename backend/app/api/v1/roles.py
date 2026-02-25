from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.auth import Role, Permission
from app.schemas.auth import RoleCreate, RoleRead, PermissionRead, AssignPermission
from app.crud.auth import create_role, create_permission, assign_permission_to_role
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/", response_model=List[RoleRead], dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


@router.post("/", response_model=RoleRead, dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def create_new_role(body: RoleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    role = create_role(db, body.name, body.description, body.company_id)
    audit_service.log(db, action="CREATE", entity_type="Role", module="AUTH", user_id=current_user.id, user_email=current_user.email, entity_id=str(role.id))
    return role


@router.get("/permissions", response_model=List[PermissionRead], dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def list_permissions(db: Session = Depends(get_db)):
    return db.query(Permission).all()


@router.post("/{role_id}/permissions", dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def assign_perm_to_role(role_id: UUID, body: AssignPermission, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    assign_permission_to_role(db, role_id, body.permission_id)
    audit_service.log(db, action="ASSIGN_PERMISSION", entity_type="Role", module="AUTH", user_id=current_user.id, user_email=current_user.email, entity_id=str(role_id))
    return {"message": "Permission assigned"}


@router.delete("/{role_id}", dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def delete_role(role_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role)
    db.commit()
    audit_service.log(db, action="DELETE", entity_type="Role", module="AUTH", user_id=current_user.id, user_email=current_user.email, entity_id=str(role_id))
    return {"message": "Role deleted"}
