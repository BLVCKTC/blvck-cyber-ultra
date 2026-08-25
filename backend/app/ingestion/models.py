from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SecurityEventEnvelope(BaseModel):
    """Immutable ingestion boundary for externally supplied security telemetry."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    tenant_id: UUID = Field(
        description="Tenant that owns the telemetry.",
    )

    source: str = Field(
        min_length=1,
        max_length=255,
        description="Originating security product or telemetry source.",
    )

    source_type: str = Field(
        min_length=1,
        max_length=100,
        description="Telemetry source type, such as EDR, IdP, or Firewall.",
    )

    received_at: datetime = Field(
        default_factory=utc_now,
        description="UTC timestamp when the telemetry was received.",
    )

    raw_payload: dict[str, Any] = Field(
        description="Original source payload.",
    )

    correlation_id: str | None = Field(
        default=None,
        max_length=255,
        description="Optional source-supplied correlation identifier.",
    )

    source_event_id: str | None = Field(
        default=None,
        max_length=255,
        description="Optional stable source-supplied event identifier.",
    )

    @field_validator("received_at")
    @classmethod
    def normalize_received_at(cls, value: datetime) -> datetime:
        """Require an actual timezone-aware timestamp and normalize it to UTC."""
        if value.utcoffset() is None:
            raise ValueError("received_at must be timezone-aware.")

        return value.astimezone(timezone.utc)

    @field_validator("raw_payload")
    @classmethod
    def validate_raw_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("raw_payload cannot be empty.")

        return value

    @field_validator("correlation_id", "source_event_id", mode="before")
    @classmethod
    def normalize_optional_identifier(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class IngestionResult(BaseModel):
    """Execution result returned by the ingestion pipeline."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID | None = None
    tenant_id: UUID
    accepted: bool
    duplicate: bool = False
    fingerprint: str | None = None
    message: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_state(self) -> IngestionResult:
        if self.duplicate and not self.accepted:
            raise ValueError("duplicate cannot be true when accepted is false.")

        return self

    @classmethod
    def accepted_event(
        cls,
        *,
        event_id: UUID,
        tenant_id: UUID,
        fingerprint: str,
    ) -> IngestionResult:
        return cls(
            event_id=event_id,
            tenant_id=tenant_id,
            accepted=True,
            fingerprint=fingerprint,
            message="Security event accepted.",
        )

    @classmethod
    def duplicate_event(
        cls,
        *,
        event_id: UUID,
        tenant_id: UUID,
        fingerprint: str,
    ) -> IngestionResult:
        return cls(
            event_id=event_id,
            tenant_id=tenant_id,
            accepted=True,
            duplicate=True,
            fingerprint=fingerprint,
            message="Duplicate security event ignored.",
        )

    @classmethod
    def rejected_event(
        cls,
        *,
        tenant_id: UUID,
        message: str,
    ) -> IngestionResult:
        return cls(
            tenant_id=tenant_id,
            accepted=False,
            message=message,
        )
