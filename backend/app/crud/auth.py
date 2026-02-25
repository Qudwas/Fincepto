from typing import Optional, Set
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.auth import User, Role, Permission, RolePermission, UserRole
from app.core.security import hash_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_permissions(db: Session, user_id: UUID) -> Set[str]:
    user = db.get(User, user_id)
    if not user:
        return set()
    if user.is_superuser:
        perms = db.query(Permission).all()
        return {p.name for p in perms}
    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    role_ids = [ur.role_id for ur in user_roles]
    if not role_ids:
        return set()
    role_perms = (
        db.query(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role_id.in_(role_ids))
        .all()
    )
    return {p.name for p in role_perms}


def create_user(db: Session, email: str, full_name: str, password: str, is_superuser: bool = False, company_id: UUID = None) -> User:
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password(password),
        is_superuser=is_superuser,
        company_id=company_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_role(db: Session, name: str, description: str = None, company_id: UUID = None) -> Role:
    role = Role(name=name, description=description, company_id=company_id)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def create_permission(db: Session, name: str, description: str = None, module: str = "SYSTEM") -> Permission:
    existing = db.query(Permission).filter(Permission.name == name).first()
    if existing:
        return existing
    perm = Permission(name=name, description=description, module=module)
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


def assign_permission_to_role(db: Session, role_id: UUID, permission_id: UUID) -> RolePermission:
    existing = db.query(RolePermission).filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id,
    ).first()
    if existing:
        return existing
    rp = RolePermission(role_id=role_id, permission_id=permission_id)
    db.add(rp)
    db.commit()
    return rp


def assign_role_to_user(db: Session, user_id: UUID, role_id: UUID) -> UserRole:
    existing = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
    ).first()
    if existing:
        return existing
    ur = UserRole(user_id=user_id, role_id=role_id)
    db.add(ur)
    db.commit()
    return ur
