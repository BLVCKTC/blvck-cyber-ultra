from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.db.repositories.security_setting_repo import SecuritySettingRepo
from app.schemas.security_setting import SecuritySettingUpdate


class SecuritySettingService:
    """Business logic for per-tenant security settings."""

    def __init__(self, db: Session):
        self.db = db
        self.security_settings = SecuritySettingRepo(db)

    def get(self, tenant_id: UUID):
        return self.security_settings.get_or_create(tenant_id)

    def update(self, tenant_id: UUID, payload: SecuritySettingUpdate):
        row = self.security_settings.get_or_create(tenant_id)
        return self.security_settings.update(
            row,
            mfa_required=payload.mfa_required,
            session_timeout_minutes=payload.session_timeout_minutes,
            settings=payload.settings,
        )