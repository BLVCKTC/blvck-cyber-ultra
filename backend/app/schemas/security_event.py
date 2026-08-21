from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel, 
    ConfigDict, 
    Field, 
    IPvAnyAddress, 
    field_validator
)
from typing_extensions import Literal


Severity = Literal["low", "medium", "high", "critical"]


class SecurityEventBase(BaseModel):
    """Common fields shared between create and read schemas."""

    timestamp: datetime
    source: str = Field(min_length=1, max_length=255)
    source_type: str = Field(min_length=1, max_length=100)
    event_type: str = Field(min_length=1, max_length=150)
    severity: Severity = "low"
    status: str = Field(default="open", min_length=1, max_length=50)
    hostname: str | None = Field(default=None, max_length=255)
    
    # Validates IPv4/IPv6 on input
    source_ip: IPvAnyAddress | None = None
    destination_ip: IPvAnyAddress | None = None

    user_identifier: str | None = Field(default=None, max_length=255)
    message: str | None = None
    raw_event: dict[str, Any] = Field(default_factory=dict)
    normalized_data: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")

    @field_validator("timestamp")
    @classmethod
    def ensure_timezone_aware(cls, v: datetime) -> datetime:
        """Reject naive datetimes to ensure unambiguous telemetry."""
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware (e.g., 2026-08-20T10:47:34Z)")
        return v


class SecurityEventCreate(SecurityEventBase):
    """
    Payload accepted from ingestion clients.
    tenant_id is strictly omitted to prevent client-side override.
    """
    model_config = ConfigDict(extra="forbid")


class SecurityEventRead(SecurityEventBase):
    """
    Schema for API responses. 
    IPs are cast to strings for Next.js and SIEM compatibility.
    """
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID
    tenant_id: UUID
    created_at: datetime

    # Overriding types to str ensures serialization is "192.168.1.50" 
    # instead of an IPv4Address object representation.
    source_ip: str | None = None
    destination_ip: str | None = None


class SecurityEventList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[SecurityEventRead]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


class SecurityEventUpdate(BaseModel):
    """
    Schema for updating an existing security event.
    All fields are optional to allow partial updates (PATCH).
    """
    status: str | None = Field(default=None, min_length=1, max_length=50)
    source: str | None = Field(default=None, min_length=1, max_length=255)
    source_type: str | None = Field(default=None, min_length=1, max_length=100)
    event_type: str | None = Field(default=None, min_length=1, max_length=150)
    severity: Severity | None = None
    hostname: str | None = Field(default=None, max_length=255)
    source_ip: IPvAnyAddress | None = None
    destination_ip: IPvAnyAddress | None = None
    user_identifier: str | None = Field(default=None, max_length=255)
    message: str | None = None
    raw_event: dict[str, Any] | None = None
    normalized_data: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")
