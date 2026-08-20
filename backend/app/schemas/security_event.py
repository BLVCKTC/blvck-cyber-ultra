from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class SecurityEventBase(BaseModel):
    """Common fields shared between create and read schemas."""
    timestamp: datetime
    source: str = Field(min_length=1, max_length=255)
    source_type: str = Field(min_length=1, max_length=100)
    event_type: str = Field(min_length=1, max_length=150)
    severity: str = Field(
        default="low", 
        pattern="^(low|medium|high|critical)$"
    )
    hostname: str | None = Field(default=None, max_length=255)
    ip_address: IPvAnyAddress | None = None
    user_identifier: str | None = Field(default=None, max_length=255)
    message: str | None = None
    raw_event: dict = Field(default_factory=dict)
    normalized_data: dict = Field(default_factory=dict)


class SecurityEventCreate(SecurityEventBase):
    """
    Payload accepted from trusted ingestion clients.
    tenant_id is derived from the authenticated session.
    """
    pass


class SecurityEventRead(SecurityEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    created_at: datetime

    # Override ip_address to str for simpler JSON serialization in responses
    ip_address: str | None


class SecurityEventList(BaseModel):
    items: list[SecurityEventRead]
    total: int
    limit: int
    offset: int
