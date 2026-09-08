from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SecuritySettingResponse(BaseModel):
    tenant_id: UUID
    mfa_required: bool
    session_timeout_minutes: int
    settings: dict = Field(default_factory=dict)
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SecuritySettingUpdate(BaseModel):
    """All fields optional — PATCH semantics, only supplied fields change."""
    mfa_required: bool | None = None
    session_timeout_minutes: int | None = Field(None, ge=5, le=43200)  # 5 min to 30 days
    settings: dict | None = None

    model_config = ConfigDict(populate_by_name=True)