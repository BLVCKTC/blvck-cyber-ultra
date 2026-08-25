from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime, ForeignKey, Index, String, Text, 
    func, UniqueConstraint, Integer, SmallInteger, CheckConstraint, text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID, INET
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EventSeverity(enum.StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(enum.StrEnum):
    OPEN = "open"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    SUPPRESSED = "suppressed"


class SecurityEvent(Base):
    """
    Tenant-scoped normalized security telemetry event.
    Events are generally immutable after ingestion.
    """
    __tablename__ = "security_events"

    __table_args__ = (
        # Prevent duplicate events from the same source
        UniqueConstraint(
            "tenant_id", "source", "source_event_id", 
            name="uq_security_events_tenant_source_event_id"
        ),
        # Database-level validation for stability and consistency
        CheckConstraint(
            f"severity IN {tuple(s.value for s in EventSeverity)}", 
            name="ck_security_events_severity"
        ),
        CheckConstraint(
            f"status IN {tuple(s.value for s in EventStatus)}", 
            name="ck_security_events_status"
        ),
        CheckConstraint(
            "risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)", 
            name="ck_security_events_risk_score"
        ),
        # Core Query Performance
        Index("ix_security_events_tenant_time", "tenant_id", "event_time"),
        Index("ix_security_events_tenant_severity_time", "tenant_id", "severity", "event_time"),
        Index("ix_security_events_normalized_data_gin", "normalized_data", postgresql_using="gin"),
        Index("ix_security_events_metadata_gin", "event_metadata", postgresql_using="gin"),
    )

    # ------------------------------------------------------------------
    # Identity & Tenancy
    # ------------------------------------------------------------------
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("tenants.id", ondelete="CASCADE"), 
        nullable=False
    )
    source_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    event_fingerprint: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # ------------------------------------------------------------------
    # Correlation
    # ------------------------------------------------------------------
    correlation_id: Mapped[str | None] = mapped_column(String(255), index=True)
    parent_event_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("security_events.id", ondelete="SET NULL")
    )

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------
    schema_version: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"))
    event_category: Mapped[str | None] = mapped_column(String(100))
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(150), nullable=False)
    
    severity: Mapped[EventSeverity] = mapped_column(
        String(20), 
        nullable=False, 
        default=EventSeverity.LOW, 
        server_default=text("'low'")
    )
    status: Mapped[EventStatus] = mapped_column(
        String(20), 
        nullable=False, 
        default=EventStatus.OPEN, 
        server_default=text("'open'")
    )
    action: Mapped[str | None] = mapped_column(String(150))
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ------------------------------------------------------------------
    # Network / Endpoint Context
    # ------------------------------------------------------------------
    source_ip: Mapped[str | None] = mapped_column(INET)
    destination_ip: Mapped[str | None] = mapped_column(INET)
    source_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    destination_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str | None] = mapped_column(String(32))
    hostname: Mapped[str | None] = mapped_column(String(255))
    user_identifier: Mapped[str | None] = mapped_column(String(255), index=True)
    process_name: Mapped[str | None] = mapped_column(String(255))
    process_id: Mapped[int | None] = mapped_column(Integer)

    # ------------------------------------------------------------------
    # MITRE ATT&CK
    # ------------------------------------------------------------------
    mitre_tactic: Mapped[str | None] = mapped_column(String(150))
    mitre_technique: Mapped[str | None] = mapped_column(String(150))
    mitre_technique_id: Mapped[str | None] = mapped_column(String(50), index=True)

    # ------------------------------------------------------------------
    # Telemetry
    # ------------------------------------------------------------------
    message: Mapped[str | None] = mapped_column(Text)
    raw_event: Mapped[dict] = mapped_column(
        JSONB, 
        nullable=False, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    normalized_data: Mapped[dict] = mapped_column(
        JSONB, 
        nullable=False, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    event_metadata: Mapped[dict] = mapped_column(
        JSONB, 
        nullable=False, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )

    def __repr__(self) -> str:
        return (
            f"<SecurityEvent id={self.id} "
            f"tenant={self.tenant_id} "
            f"type={self.event_type} "
            f"severity={self.severity} "
            f"time={self.event_time}>"
        )
