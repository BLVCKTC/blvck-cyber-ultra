from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.audit_log_entry import AuditLogEntry


def record_audit_event(
    db: Session,
    *,
    tenant_id: UUID,
    actor_user_id: UUID | None,
    action: str,
    entity_type: str,
    entity_id: UUID | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    """Write one audit entry.

    Deliberately does not call db.commit() — this is meant to run inside
    the same transaction as the write it's recording, so a failure
    partway through the surrounding operation rolls the audit entry back
    too rather than leaving an audit record for a change that never
    actually happened.

    `action` follows a "resource.verb" convention matching the existing
    permission-key naming already used throughout the app (e.g.
    "security_settings.updated", "team.created", "api_key.revoked") so
    audit actions and permission keys stay readable side by side.
    """
    db.add(
        AuditLogEntry(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload or {},
        )
    )