from __future__ import annotations

from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.security_event import SecurityEvent


class SecurityEventRepository:
    """
    Tenant-scoped repository for SecurityEvent.
    All methods enforce tenant_id isolation.
    """

    def __init__(self, db: Session):
        self.db = db

    def get(self, *, tenant_id: UUID, event_id: UUID) -> SecurityEvent | None:
        return self.db.scalar(
            select(SecurityEvent).where(
                SecurityEvent.id == event_id,
                SecurityEvent.tenant_id == tenant_id,
            )
        )

    def count(self, *, tenant_id: UUID) -> int:
        return self.db.scalar(
            select(func.count()).select_from(SecurityEvent).where(
                SecurityEvent.tenant_id == tenant_id
            )
        ) or 0

    def list(
        self,
        *,
        tenant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        severity: str | None = None,
        event_type: str | None = None,
        source: str | None = None,
    ) -> list[SecurityEvent]:
        
        # Use a list of filters to avoid repetitive 'if' blocks
        filters = [SecurityEvent.tenant_id == tenant_id]
        
        if severity:
            filters.append(SecurityEvent.severity == severity)
        if event_type:
            filters.append(SecurityEvent.event_type == event_type)
        if source:
            filters.append(SecurityEvent.source == source)

        query = (
            select(SecurityEvent)
            .where(*filters)
            .order_by(SecurityEvent.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(self.db.scalars(query).all())

    def create(self, *, tenant_id: UUID, data: dict) -> SecurityEvent:
        """
        Expects 'data' to be a dictionary (e.g., from SecurityEventCreate.model_dump()).
        """
        event = SecurityEvent(
            tenant_id=tenant_id,
            **data
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
