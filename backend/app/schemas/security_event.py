from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    IPvAnyAddress,
    field_validator,
)


# Using Literals here ensures the OpenAPI/Swagger docs show a dropdown 
# of allowed values, mirroring the DB CheckConstraints.
SecurityEventSeverity = Literal[
    "info",
    "low",
    "medium",
    "high",
    "critical",
]

SecurityEventStatus = Literal[
    "open",
    "processing",
    "processed",
    "failed",
    "suppressed",
]


class SecurityEventBase(BaseModel):
    """
    Common security-event fields.
    Mirrors the SecurityEvent database model.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    # --- Source Identity & Deduplication ---
    source_event_id: str | None = Field(
        default=None,
        max_length=255,
        description="Stable identifier supplied by the originating system.",
    )
    event_fingerprint: str | None = Field(
        default=None,
        max_length=128,
        description="Deterministic hash used for deduplication when source_event_id is missing.",
    )

    # --- Correlation ---
    correlation_id: str | None = Field(
        default=None,
        max_length=255,
        description="Links related events into a single attack timeline.",
    )
    parent_event_id: UUID | None = Field(
        default=None,
        description="Reference to the causal parent event.",
    )

    # --- Timing ---
    event_time: datetime = Field(
        ..., 
        description="Time the event occurred at the source. Must be timezone-aware.",
    )

    # --- Classification ---
    schema_version: int = Field(
        default=1,
        ge=1,
        description="Normalized event schema version.",
    )
    event_category: str | None = Field(
        default=None,
        max_length=100,
        description="High-level category (e.g., 'Authentication', 'Network').",
    )
    source: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="The security product (e.g., 'CrowdStrike', 'Okta')."
    )
    source_type: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Product type (e.g., 'EDR', 'IdP', 'Firewall')."
    )
    event_type: str = Field(
        ..., 
        min_length=1, 
        max_length=150, 
        description="The normalized event action (e.g., 'process_created')."
    )
    severity: SecurityEventSeverity = Field(
        default="low",
    )
    status: SecurityEventStatus = Field(
        default="open",
    )
    action: str | None = Field(
        default=None,
        max_length=150,
        description="Observed action (e.g., 'blocked', 'allowed').",
    )
    risk_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Risk score normalized from 0 to 100.",
    )

    # --- Network / Endpoint Context ---
    # IPvAnyAddress validates both IPv4 and IPv6, mapping perfectly to Postgres INET
    source_ip: IPvAnyAddress | None = Field(default=None)
    destination_ip: IPvAnyAddress | None = Field(default=None)
    source_port: int | None = Field(default=None, ge=0, le=65535)
    destination_port: int | None = Field(default=None, ge=0, le=65535)
    protocol: str | None = Field(default=None, max_length=32)
    hostname: str | None = Field(default=None, max_length=255)
    user_identifier: str | None = Field(default=None, max_length=255)
    process_name: str | None = Field(default=None, max_length=255)
    process_id: int | None = Field(default=None, ge=0)

    # --- MITRE ATT&CK ---
    mitre_tactic: str | None = Field(default=None, max_length=150)
    mitre_technique: str | None = Field(default=None, max_length=150)
    mitre_technique_id: str | None = Field(default=None, max_length=50)

    # --- Telemetry ---
    message: str | None = Field(default=None)
    raw_event: dict[str, Any] = Field(
        default_factory=dict,
        description="Immutable original log for forensic auditing.",
    )
    normalized_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Normalized ECS-style data for detection engines.",
    )
    event_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Internal enrichment and platform tags.",
    )

    @field_validator("event_time")
    @classmethod
    def validate_event_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("event_time must be timezone-aware (e.g., UTC)")
        return value


class SecurityEventCreate(SecurityEventBase):
    """
    Payload for event ingestion.
    tenant_id is omitted as it is derived from the auth context.
    """
    pass


class SecurityEventRead(SecurityEventBase):
    """
    Schema for API responses.
    """
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    id: UUID
    tenant_id: UUID
    ingested_at: datetime
    created_at: datetime


class SecurityEventList(BaseModel):
    """
    Paginated response for security events.
    """
    model_config = ConfigDict(extra="forbid")

    items: list[SecurityEventRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=500)
    offset: int = Field(ge=0)


class SecurityEventUpdate(BaseModel):
    """
    Restricted update schema.
    Telemetry is immutable; only processing status and metadata can be mutated.
    """
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    status: SecurityEventStatus | None = None
    event_metadata: dict[str, Any] | None = None
