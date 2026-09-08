from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.security_setting import SecuritySetting


class SecuritySettingRepo:
    """Repository for the per-tenant security settings singleton."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, tenant_id: UUID) -> SecuritySetting | None:
        return self.db.get(SecuritySetting, tenant_id)

    def get_or_create(self, tenant_id: UUID) -> SecuritySetting:
        """Return the tenant's settings row, creating one with column
        defaults (mfa_required=false, session_timeout_minutes=480) if it
        doesn't exist yet. A tenant that's never touched this page should
        still get a sensible response, not a 404."""
        existing = self.get(tenant_id)
        if existing is not None:
            return existing

        row = SecuritySetting(tenant_id=tenant_id)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def update(
        self,
        row: SecuritySetting,
        *,
        mfa_required: bool | None,
        session_timeout_minutes: int | None,
        settings: dict | None,
    ) -> SecuritySetting:
        if mfa_required is not None:
            row.mfa_required = mfa_required
        if session_timeout_minutes is not None:
            row.session_timeout_minutes = session_timeout_minutes
        if settings is not None:
            row.settings = settings

        self.db.commit()
        self.db.refresh(row)
        return row