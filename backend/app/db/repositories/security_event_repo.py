from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.db.models.security_event import SecurityEvent


class SecurityEventRepository:
    """
    Persistence repository for tenant-scoped security events.

    Tenant isolation is enforced in every read and write operation.
    """

    _PROTECTED_FIELDS = frozenset(
        {
            "id",
            "tenant_id",
            "created_at",
            "updated_at",
        }
    )

    _FILTERABLE_FIELDS = {
        "severity": SecurityEvent.severity,
        "status": SecurityEvent.status,
        "event_category": SecurityEvent.event_category,
        "event_type": SecurityEvent.event_type,
        "source": SecurityEvent.source,
        "source_type": SecurityEvent.source_type,
        "hostname": SecurityEvent.hostname,
        "user_identifier": SecurityEvent.user_identifier,
        "mitre_technique_id": SecurityEvent.mitre_technique_id,
    }

    _SEARCHABLE_FIELDS = (
        SecurityEvent.source,
        SecurityEvent.source_type,
        SecurityEvent.event_category,
        SecurityEvent.event_type,
        SecurityEvent.hostname,
        SecurityEvent.user_identifier,
        SecurityEvent.process_name,
        SecurityEvent.mitre_tactic,
        SecurityEvent.mitre_technique,
        SecurityEvent.mitre_technique_id,
        SecurityEvent.message,
        SecurityEvent.correlation_id,
        SecurityEvent.source_event_id,
    )

    _MODEL_COLUMNS = frozenset(SecurityEvent.__table__.columns.keys())

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Validation and filters
    # ------------------------------------------------------------------

    @classmethod
    def _validate_data(
        cls,
        data: Mapping[str, Any],
        *,
        operation: str,
    ) -> dict[str, Any]:
        values = dict(data)

        unknown_fields = set(values) - cls._MODEL_COLUMNS
        if unknown_fields:
            fields = ", ".join(sorted(unknown_fields))
            raise ValueError(
                f"Unknown fields for SecurityEvent {operation}: {fields}"
            )

        protected_fields = set(values) & cls._PROTECTED_FIELDS
        if protected_fields:
            fields = ", ".join(sorted(protected_fields))
            raise ValueError(
                f"Protected fields cannot be modified: {fields}"
            )

        return values

    @staticmethod
    def _escape_like(value: str) -> str:
        """Escape LIKE wildcards while preserving literal search semantics."""
        return (
            value.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )

    def _build_filters(
        self,
        *,
        tenant_id: UUID,
        filters: Mapping[str, Any],
    ) -> list[ColumnElement[bool]]:
        criteria: list[ColumnElement[bool]] = [
            SecurityEvent.tenant_id == tenant_id,
        ]

        for key, column in self._FILTERABLE_FIELDS.items():
            value = filters.get(key)

            if value is not None and value != "":
                criteria.append(column == value)

        query = filters.get("q")
        if isinstance(query, str):
            query = query.strip()

        if query:
            pattern = f"%{self._escape_like(query)}%"

            criteria.append(
                or_(
                    *(
                        column.ilike(pattern, escape="\\")
                        for column in self._SEARCHABLE_FIELDS
                    )
                )
            )

        start_time = filters.get("start_time")
        end_time = filters.get("end_time")

        if (
            start_time is not None
            and end_time is not None
            and start_time > end_time
        ):
            raise ValueError("start_time must be earlier than end_time")

        if start_time is not None:
            criteria.append(SecurityEvent.event_time >= start_time)

        if end_time is not None:
            criteria.append(SecurityEvent.event_time <= end_time)

        return criteria

    # ------------------------------------------------------------------
    # Get
    # ------------------------------------------------------------------

    def get(
        self,
        *,
        tenant_id: UUID,
        event_id: UUID,
    ) -> SecurityEvent | None:
        statement = select(SecurityEvent).where(
            SecurityEvent.id == event_id,
            SecurityEvent.tenant_id == tenant_id,
        )

        return self.db.scalar(statement)

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def list(
        self,
        *,
        tenant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        **filters: Any,
    ) -> list[SecurityEvent]:
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        if offset < 0:
            raise ValueError("offset must be greater than or equal to zero")

        statement = (
            select(SecurityEvent)
            .where(
                *self._build_filters(
                    tenant_id=tenant_id,
                    filters=filters,
                )
            )
            .order_by(
                SecurityEvent.event_time.desc(),
                SecurityEvent.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        return list(self.db.scalars(statement).all())

    # ------------------------------------------------------------------
    # Count
    # ------------------------------------------------------------------

    def count(
        self,
        *,
        tenant_id: UUID,
        **filters: Any,
    ) -> int:
        statement = select(func.count()).select_from(SecurityEvent).where(
            *self._build_filters(
                tenant_id=tenant_id,
                filters=filters,
            )
        )

        return int(self.db.scalar(statement) or 0)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(
        self,
        *,
        tenant_id: UUID,
        data: Mapping[str, Any],
    ) -> SecurityEvent:
        values = self._validate_data(data, operation="create")

        event = SecurityEvent(
            tenant_id=tenant_id,
            **values,
        )

        return self._commit_and_return(event)

    # ------------------------------------------------------------------
    # Bulk create
    # ------------------------------------------------------------------

    def create_many(
        self,
        *,
        tenant_id: UUID,
        data: list[Mapping[str, Any]],
    ) -> list[SecurityEvent]:
        if not data:
            return []

        events = [
            SecurityEvent(
                tenant_id=tenant_id,
                **self._validate_data(item, operation="create"),
            )
            for item in data
        ]

        try:
            self.db.add_all(events)
            self.db.commit()

            for event in events:
                self.db.refresh(event)

            return events

        except Exception:
            self.db.rollback()
            raise

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(
        self,
        *,
        tenant_id: UUID,
        event_id: UUID,
        data: Mapping[str, Any],
    ) -> SecurityEvent | None:
        values = self._validate_data(data, operation="update")

        if not values:
            raise ValueError("update data must contain at least one field")

        event = self.get(
            tenant_id=tenant_id,
            event_id=event_id,
        )

        if event is None:
            return None

        for field, value in values.items():
            setattr(event, field, value)

        return self._commit_and_return(event)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(
        self,
        *,
        tenant_id: UUID,
        event_id: UUID,
    ) -> bool:
        statement = delete(SecurityEvent).where(
            SecurityEvent.id == event_id,
            SecurityEvent.tenant_id == tenant_id,
        )

        try:
            result = self.db.execute(statement)
            self.db.commit()
            return bool(result.rowcount and result.rowcount > 0)

        except Exception:
            self.db.rollback()
            raise

    # ------------------------------------------------------------------
    # Transaction helper
    # ------------------------------------------------------------------

    def _commit_and_return(
        self,
        event: SecurityEvent,
    ) -> SecurityEvent:
        try:
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            return event

        except Exception:
            self.db.rollback()
            raise
