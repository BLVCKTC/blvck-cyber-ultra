from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.db.models.security_event import SecurityEvent


class SecurityEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def _build_filters(
        self,
        tenant_id: UUID,
        **filters,
    ) -> list[ColumnElement[bool]]:
        criteria = [SecurityEvent.tenant_id == tenant_id]
        
        # Equality mapping
        mapping = {
            "severity": SecurityEvent.severity,
            "event_type": SecurityEvent.event_type,
            "source": SecurityEvent.source,
            "hostname": SecurityEvent.hostname,
        }
        for key, column in mapping.items():
            if value := filters.get(key):
                criteria.append(column == value)

        if q := filters.get("q"):
            pattern = f"%{q.strip()}%"
            criteria.append(or_(
                SecurityEvent.source.ilike(pattern),
                SecurityEvent.source_type.ilike(pattern),
                SecurityEvent.event_type.ilike(pattern),
                SecurityEvent.hostname.ilike(pattern),
                SecurityEvent.user_identifier.ilike(pattern),
                SecurityEvent.message.ilike(pattern),
            ))

        # Range mapping
        if start_time := filters.get("start_time"):
            criteria.append(SecurityEvent.timestamp >= start_time)
        if end_time := filters.get("end_time"):
            criteria.append(SecurityEvent.timestamp <= end_time)

        return criteria

    def get(self, *, tenant_id: UUID, event_id: UUID) -> SecurityEvent | None:
        return self.db.scalar(
            select(SecurityEvent).where(
                SecurityEvent.id == event_id,
                SecurityEvent.tenant_id == tenant_id,
            )
        )

    def list(self, *, tenant_id: UUID, limit: int = 50, offset: int = 0, **filters) -> list[SecurityEvent]:
        query = (
            select(SecurityEvent)
            .where(*self._build_filters(tenant_id, **filters))
            .order_by(SecurityEvent.timestamp.desc(), SecurityEvent.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.db.scalars(query).all()

    def count(self, *, tenant_id: UUID, **filters) -> int:
        query = select(func.count(SecurityEvent.id)).where(*self._build_filters(tenant_id, **filters))
        return self.db.scalar(query) or 0

    def create(self, *, tenant_id: UUID, data: dict) -> SecurityEvent:
        event = SecurityEvent(tenant_id=tenant_id, **data)
        return self._commit_and_return(event)

    def create_many(self, *, tenant_id: UUID, data: list[dict]) -> list[SecurityEvent]:
        events = [SecurityEvent(tenant_id=tenant_id, **item) for item in data]
        try:
            self.db.add_all(events)
            self.db.commit()
            # Removed the refresh() loop to prevent N+1 database roundtrips.
            return events
        except Exception:
            self.db.rollback()
            raise

    def _commit_and_return(self, obj: SecurityEvent) -> SecurityEvent:
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception:
            self.db.rollback()
            raise

    def update(self, *, tenant_id: UUID, event_id: UUID, data: dict) -> SecurityEvent | None:
        event = self.get(tenant_id=tenant_id, event_id=event_id)
        if event is None:
            return None
        for key, value in data.items():
            setattr(event, key, value)
        return self._commit_and_return(event)

    def delete(self, *, tenant_id: UUID, event_id: UUID) -> bool:
        try:
            stmt = delete(SecurityEvent).where(
                SecurityEvent.id == event_id, 
                SecurityEvent.tenant_id == tenant_id
            )
            result = self.db.execute(stmt)
            self.db.commit()
            return bool(result.rowcount)
        except Exception:
            self.db.rollback()
            raise
