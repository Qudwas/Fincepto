from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str
    is_active: bool = True
    is_superuser: bool = False
    company_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    company_id: Optional[UUID] = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    company_id: Optional[UUID] = None
    created_at: datetime


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    company_id: Optional[UUID] = None


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    company_id: Optional[UUID] = None


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    module: str


class AssignRole(BaseModel):
    role_id: UUID


class AssignPermission(BaseModel):
    permission_id: UUID
