from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.security_event import SecurityEvent
from app.db.repositories.security_event_repo import SecurityEventRepository
from app.schemas.security_event import SecurityEventCreate, SecurityEventUpdate


class SecurityEventService:
    """Tenant-scoped application service for security events."""

    DEFAULT_LIMIT = 50
    MAX_LIMIT = 500

    def __init__(self, db: Session) -> None:
        self.events = SecurityEventRepository(db)

    @staticmethod
    def _validate_pagination(limit: int, offset: int) -> None:
        if not 1 <= limit <= SecurityEventService.MAX_LIMIT:
            raise ValueError(
                f"limit must be between 1 and "
                f"{SecurityEventService.MAX_LIMIT}"
            )

        if offset < 0:
            raise ValueError(
                "offset must be greater than or equal to 0"
            )

    @staticmethod
    def _build_filters(
        *,
        q: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        event_category: str | None = None,
        event_type: str | None = None,
        source: str | None = None,
        source_type: str | None = None,
        hostname: str | None = None,
        user_identifier: str | None = None,
        mitre_technique_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, Any]:
        return {
            "q": q,
            "severity": severity,
            "status": status,
            "event_category": event_category,
            "event_type": event_type,
            "source": source,
            "source_type": source_type,
            "hostname": hostname,
            "user_identifier": user_identifier,
            "mitre_technique_id": mitre_technique_id,
            "start_time": start_time,
            "end_time": end_time,
        }
    
    def create(
        self,
        *,
        tenant_id: UUID,
        payload: SecurityEventCreate,
    ) -> SecurityEvent:
        """
        Create a tenant-scoped security event.

        Tenant identity is supplied separately from the payload so that
        persistence cannot accidentally trust a tenant_id from telemetry.
        """
        # Use Python mode so UUIDs and datetimes remain ORM-native values.
        data = payload.model_dump(
            mode="python",
            exclude_none=False,
        )

        return self.events.create(
            tenant_id=tenant_id,
            data=data,
        )

    def get(
        self,
        *,
        tenant_id: UUID,
        event_id: UUID,
    ) -> SecurityEvent | None:
        """Get one event by ID within the authenticated tenant."""
        return self.events.get(
            tenant_id=tenant_id,
            event_id=event_id,
        )

    def get_by_source_event_id(
        self,
        *,
        tenant_id: UUID,
        source: str,
        source_event_id: str,
    ) -> SecurityEvent | None:
        """
        Find an existing event using the source's stable event ID.

        The lookup is always tenant-scoped.
        """
        return self.events.get_by_source_event_id(
            tenant_id=tenant_id,
            source=source,
            source_event_id=source_event_id,
        )

    def get_by_fingerprint(
        self,
        *,
        tenant_id: UUID,
        fingerprint: str,
    ) -> SecurityEvent | None:
        """
        Find an existing event using its deterministic fingerprint.

        The lookup is always tenant-scoped.
        """
        return self.events.get_by_fingerprint(
            tenant_id=tenant_id,
            fingerprint=fingerprint,
        )

    def list(
        self,
        *,
        tenant_id: UUID,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        q: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        event_category: str | None = None,
        event_type: str | None = None,
        source: str | None = None,
        source_type: str | None = None,
        hostname: str | None = None,
        user_identifier: str | None = None,
        mitre_technique_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> tuple[list[SecurityEvent], int]:
        """List security events within the authenticated tenant."""
        self._validate_pagination(limit, offset)

        filters = self._build_filters(
            q=q,
            severity=severity,
            status=status,
            event_category=event_category,
            event_type=event_type,
            source=source,
            source_type=source_type,
            hostname=hostname,
            user_identifier=user_identifier,
            mitre_technique_id=mitre_technique_id,
            start_time=start_time,
            end_time=end_time,
        )

        items = self.events.list(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            **filters,
        )

        total = self.events.count(
            tenant_id=tenant_id,
            **filters,
        )

        return items, total

    def update(
        self,
        *,
        tenant_id: UUID,
        event_id: UUID,
        payload: SecurityEventUpdate,
    ) -> SecurityEvent | None:
        """
        Update an event within the authenticated tenant.

        Only fields permitted by SecurityEventUpdate can be changed.
        """
        # Preserve explicitly supplied null values for PATCH semantics.
        data = payload.model_dump(
            mode="python",
            exclude_unset=True,
        )

        if not data:
            raise ValueError(
                "update payload must contain at least one field"
            )

        return self.events.update(
            tenant_id=tenant_id,
            event_id=event_id,
            data=data,
        )

    def delete(
        self,
        *,
        tenant_id: UUID,
        event_id: UUID,
    ) -> bool:
        """Delete an event within the authenticated tenant."""
        return self.events.delete(
            tenant_id=tenant_id,
            event_id=event_id,
        )