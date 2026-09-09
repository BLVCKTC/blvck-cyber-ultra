from __future__ import annotations

from unittest import result
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.repositories.security_setting_repo import SecuritySettingRepo
from app.schemas.security_setting import SecuritySettingUpdate
from app.services.audit_service import record_audit_event


class SecuritySettingService:
    """Business logic for per-tenant security settings."""

    def __init__(self, db: Session):
        self.db = db
        self.security_settings = SecuritySettingRepo(db)

    def get(self, tenant_id: UUID):
        return self.security_settings.get_or_create(tenant_id)

    def update(self, tenant_id: UUID, payload: SecuritySettingUpdate, *, actor_user_id: UUID):
        row = self.security_settings.get_or_create(tenant_id)
        changed_fields = payload.model_dump(exclude_unset=True)
        result = self.security_settings.update(
            row,
            mfa_required=payload.mfa_required,
            session_timeout_minutes=payload.session_timeout_minutes,
            settings=payload.settings,
    )
        record_audit_event(
            self.db,
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="security_settings.updated",
            entity_type="security_setting",
        entity_id=tenant_id,
        payload={"changed_fields": changed_fields},
    )
        return result