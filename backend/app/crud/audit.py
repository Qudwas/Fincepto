from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.audit import AuditLog


def create_audit_log(
    db: Session,
    action: str,
    entity_type: str,
    module: str,
    user_id: Optional[UUID] = None,
    user_email: str = "system",
    entity_id: Optional[str] = None,
    before_state: Optional[dict] = None,
    after_state: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    company_id: Optional[UUID] = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        user_email=user_email,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        module=module,
        before_state=before_state,
        after_state=after_state,
        ip_address=ip_address,
        user_agent=user_agent,
        company_id=company_id,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_audit_logs(
    db: Session,
    module: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[UUID] = None,
    company_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[AuditLog]:
    query = db.query(AuditLog)
    if module:
        query = query.filter(AuditLog.module == module)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if company_id:
        query = query.filter(AuditLog.company_id == company_id)
    if from_date:
        query = query.filter(AuditLog.timestamp >= from_date)
    if to_date:
        query = query.filter(AuditLog.timestamp <= to_date)
    if action:
        query = query.filter(AuditLog.action == action)
    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
