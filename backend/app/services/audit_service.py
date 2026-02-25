from typing import Optional
from uuid import UUID
from fastapi import Request
from sqlalchemy.orm import Session
from app.crud.audit import create_audit_log


class AuditService:
    @staticmethod
    def log(
        db: Session,
        action: str,
        entity_type: str,
        module: str,
        user_id: Optional[UUID] = None,
        user_email: str = "system",
        entity_id: Optional[str] = None,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
        request: Optional[Request] = None,
        company_id: Optional[UUID] = None,
    ):
        ip_address = None
        user_agent = None
        if request:
            forwarded = request.headers.get("X-Forwarded-For")
            ip_address = forwarded.split(",")[0] if forwarded else request.client.host if request.client else None
            user_agent = request.headers.get("User-Agent")

        return create_audit_log(
            db=db,
            action=action,
            entity_type=entity_type,
            module=module,
            user_id=user_id,
            user_email=user_email,
            entity_id=entity_id,
            before_state=before_state,
            after_state=after_state,
            ip_address=ip_address,
            user_agent=user_agent,
            company_id=company_id,
        )


audit_service = AuditService()
