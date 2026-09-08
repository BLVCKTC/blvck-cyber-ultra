from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security.api_key_hash import generate_api_key
from app.db.models.api_key import ApiKey
from app.db.repositories.api_key_repo import ApiKeyRepo
from app.schemas.api_key import ApiKeyCreate


class ApiKeyService:
    def __init__(self, db: Session):
        self.db = db
        self.api_keys = ApiKeyRepo(db)

    def _get_required_key(self, key_id: UUID, tenant_id: UUID) -> ApiKey:
        row = self.api_keys.get_by_id(key_id)
        if row is None or row.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="api_key_not_found")
        return row

    def list_keys(self, tenant_id: UUID) -> list[ApiKey]:
        return self.api_keys.list_for_tenant(tenant_id)

    def create_key(self, tenant_id: UUID, created_by: UUID, payload: ApiKeyCreate):
        raw_key, key_prefix, key_hash = generate_api_key()
        row = self.api_keys.create(
            tenant_id=tenant_id,
            created_by=created_by,
            name=payload.name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            scopes=payload.scopes,
        )
        # The raw key is attached here, transiently, only for this one
        # response — it is never written to the row or persisted anywhere.
        return row, raw_key

    def revoke_key(self, key_id: UUID, tenant_id: UUID) -> ApiKey:
        row = self._get_required_key(key_id, tenant_id)
        if row.revoked_at is not None:
            raise HTTPException(status_code=409, detail="already_revoked")
        return self.api_keys.revoke(row)