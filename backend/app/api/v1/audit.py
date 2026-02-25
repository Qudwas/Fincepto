from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_permission
from app.crud.audit import get_audit_logs
from app.schemas.audit import AuditLogRead

router = APIRouter()


@router.get("/logs", response_model=List[AuditLogRead], dependencies=[Depends(require_permission("AUDIT_VIEW"))])
def list_audit_logs(
    module: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[UUID] = None,
    company_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return get_audit_logs(db, module, entity_type, user_id, company_id, from_date, to_date, action, skip, limit)
