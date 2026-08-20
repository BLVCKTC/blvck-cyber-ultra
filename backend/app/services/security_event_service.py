from __future__ import annotations

from uuid import UUID
from sqlalchemy.orm import Session

from app.db.repositories.security_event_repo import SecurityEventRepository
from app.schemas.security_event import SecurityEventCreate


class SecurityEventService:
    """
    Application service for security events.
    Tenant ownership is supplied by the authenticated membership.
    """

    def __init__(self, db: Session):
        self.db = db
        self.events = SecurityEventRepository(db)

    def create(self, *, tenant_id: UUID, payload: SecurityEventCreate):
        # model_dump(mode='json') converts IPvAnyAddress and UUIDs to strings automatically
        return self.events.create(
            tenant_id=tenant_id, 
            data=payload.model_dump(mode='json')
        )

    def get(self, *, tenant_id: UUID, event_id: UUID):
        return self.events.get(tenant_id=tenant_id, event_id=event_id)

    def list(
        self,
        *,
        tenant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        severity: str | None = None,
        event_type: str | None = None,
        source: str | None = None,
    ):
        items = self.events.list(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            severity=severity,
            event_type=event_type,
            source=source,
        )
        total = self.events.count(tenant_id=tenant_id)
        
        return items, total
