from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    scopes: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class ApiKeyCreateResponse(BaseModel):
    """Returned ONLY once, at creation time — the raw key is never
    retrievable again after this response."""
    id: UUID
    name: str
    key_prefix: str
    api_key: str  # the full raw secret — shown once, never stored raw
    scopes: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ApiKeyResponse(BaseModel):
    """Used everywhere else — list, get. Never includes the raw key
    or the hash, only enough to identify and manage the key."""
    id: UUID
    name: str
    key_prefix: str
    scopes: list[str]
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ApiKeyListResponse(BaseModel):
    items: list[ApiKeyResponse]
    total: int = Field(..., ge=0)

    model_config = ConfigDict(populate_by_name=True)