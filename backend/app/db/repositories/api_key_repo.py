from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.api_key import ApiKey


class ApiKeyRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, key_id: UUID) -> ApiKey | None:
        return self.db.get(ApiKey, key_id)

    def list_for_tenant(self, tenant_id: UUID) -> list[ApiKey]:
        return list(
            self.db.scalars(
                select(ApiKey)
                .where(ApiKey.tenant_id == tenant_id)
                .order_by(ApiKey.created_at.desc())
            )
        )

    def create(
        self,
        *,
        tenant_id: UUID,
        created_by: UUID,
        name: str,
        key_prefix: str,
        key_hash: str,
        scopes: list[str],
    ) -> ApiKey:
        row = ApiKey(
            tenant_id=tenant_id,
            created_by=created_by,
            name=name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            scopes=scopes,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def revoke(self, row: ApiKey) -> ApiKey:
        row.revoked_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(row)
        return row