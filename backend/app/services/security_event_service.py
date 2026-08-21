from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.security_event import SecurityEvent
from app.db.repositories.security_event_repo import SecurityEventRepository
from app.schemas.security_event import SecurityEventCreate


class SecurityEventService:
    def __init__(self, db: Session):
        self.db = db
        self.events = SecurityEventRepository(db)

    def create(self, *, tenant_id: UUID, payload: SecurityEventCreate) -> SecurityEvent:
        return self.events.create(
            tenant_id=tenant_id, 
            data=payload.model_dump(mode="json")
        )

    def get(self, *, tenant_id: UUID, event_id: UUID) -> SecurityEvent | None:
        return self.events.get(tenant_id=tenant_id, event_id=event_id)

    def list(
        self,
        *,
        tenant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        **filters,
    ) -> tuple[list[SecurityEvent], int]:
        items = self.events.list(
            tenant_id=tenant_id, 
            limit=limit, 
            offset=offset, 
            **filters
        )
        total = self.events.count(tenant_id=tenant_id, **filters)
        return items, total

    def delete(self, *, tenant_id: UUID, event_id: UUID) -> bool:
        return self.events.delete(tenant_id=tenant_id, event_id=event_id)
