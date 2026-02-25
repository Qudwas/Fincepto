from uuid import UUID
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: Optional[UUID] = None
    user_email: str
    timestamp: datetime
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    module: str
    before_state: Optional[Any] = None
    after_state: Optional[Any] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    company_id: Optional[UUID] = None
