from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.auth import User
from app.schemas.auth import UserCreate, UserUpdate, UserRead, AssignRole
from app.crud.auth import create_user, assign_role_to_user
from app.core.security import hash_password
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/", response_model=List[UserRead], dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()


@router.post("/", response_model=UserRead, dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def create_new_user(body: UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from app.crud.auth import get_user_by_email
    if get_user_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, body.email, body.full_name, body.password, body.is_superuser, body.company_id)
    audit_service.log(db, action="CREATE", entity_type="User", module="AUTH", user_id=current_user.id, user_email=current_user.email, entity_id=str(user.id), after_state={"email": user.email})
    return user


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def update_user(user_id: UUID, body: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    before = {"email": user.email, "is_active": user.is_active}
    if body.email:
        user.email = body.email
    if body.full_name:
        user.full_name = body.full_name
    if body.password:
        user.hashed_password = hash_password(body.password)
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.company_id is not None:
        user.company_id = body.company_id
    db.commit()
    db.refresh(user)
    audit_service.log(db, action="UPDATE", entity_type="User", module="AUTH", user_id=current_user.id, user_email=current_user.email, entity_id=str(user.id), before_state=before)
    return user


@router.delete("/{user_id}", dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def delete_user(user_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    audit_service.log(db, action="DEACTIVATE", entity_type="User", module="AUTH", user_id=current_user.id, user_email=current_user.email, entity_id=str(user_id))
    return {"message": "User deactivated"}


@router.post("/{user_id}/roles", dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def assign_role(user_id: UUID, body: AssignRole, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    assign_role_to_user(db, user_id, body.role_id)
    audit_service.log(db, action="ASSIGN_ROLE", entity_type="User", module="AUTH", user_id=current_user.id, user_email=current_user.email, entity_id=str(user_id), after_state={"role_id": str(body.role_id)})
    return {"message": "Role assigned"}
