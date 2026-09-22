from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.quarantined_event import QuarantinedEvent


class QuarantinedEventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        tenant_id: UUID,
        source: str,
        source_type: str,
        failure_stage: str,
        failure_reason: str,
        raw_payload: dict[str, Any],
        received_at: datetime,
        partial_normalized: dict[str, Any] | None = None,
    ) -> QuarantinedEvent:
        quarantine = QuarantinedEvent(
            tenant_id=tenant_id,
            source=source,
            source_type=source_type,
            failure_stage=failure_stage,
            failure_reason=failure_reason,
            raw_payload=raw_payload,
            partial_normalized=partial_normalized,
            received_at=received_at,
        )

        self.db.add(quarantine)
        self.db.flush()

        return quarantine

    def get(
        self,
        *,
        tenant_id: UUID,
        quarantine_id: UUID,
    ) -> QuarantinedEvent | None:
        stmt = select(QuarantinedEvent).where(
            QuarantinedEvent.id == quarantine_id,
            QuarantinedEvent.tenant_id == tenant_id,
        )

        return self.db.scalar(stmt)

    def list_unresolved(
        self,
        *,
        tenant_id: UUID | None = None,
        limit: int = 100,
    ) -> list[QuarantinedEvent]:
        stmt = (
            select(QuarantinedEvent)
            .where(QuarantinedEvent.resolved_at.is_(None))
            .order_by(QuarantinedEvent.quarantined_at.desc())
            .limit(limit)
        )

        if tenant_id is not None:
            stmt = stmt.where(
                QuarantinedEvent.tenant_id == tenant_id,
            )

        return list(self.db.scalars(stmt).all())

    def list(
        self,
        *,
        tenant_id: UUID,
        unresolved_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[QuarantinedEvent]:
        stmt = (
            select(QuarantinedEvent)
            .where(
                QuarantinedEvent.tenant_id == tenant_id,
            )
            .order_by(QuarantinedEvent.quarantined_at.desc())
            .offset(offset)
            .limit(limit)
        )

        if unresolved_only:
            stmt = stmt.where(
                QuarantinedEvent.resolved_at.is_(None),
            )

        return list(self.db.scalars(stmt).all())

    def resolve(
        self,
        *,
        tenant_id: UUID,
        quarantine_id: UUID,
        resolution_note: str | None = None,
    ) -> QuarantinedEvent | None:
        quarantine = self.get(
            tenant_id=tenant_id,
            quarantine_id=quarantine_id,
        )

        if quarantine is None:
            return None

        quarantine.resolved_at = datetime.now(timezone.utc)
        quarantine.resolution_note = resolution_note

        self.db.flush()

        return quarantine

    def delete(
        self,
        *,
        tenant_id: UUID,
        quarantine_id: UUID,
    ) -> bool:
        quarantine = self.get(
            tenant_id=tenant_id,
            quarantine_id=quarantine_id,
        )

        if quarantine is None:
            return False

        self.db.delete(quarantine)
        self.db.flush()

        return True