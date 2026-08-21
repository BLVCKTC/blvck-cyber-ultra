from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SecurityEvent(Base):
    """
    Tenant-scoped normalized security event.

    Security events are the foundational telemetry objects
    used by detections, alerts, investigations, and threat hunting.
    """

    __tablename__ = "security_events"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="low",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="open",
        server_default="open",
    )

    hostname: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    source_ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    destination_ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    user_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    raw_event: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    normalized_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index(
            "ix_security_events_tenant_timestamp",
            "tenant_id",
            "timestamp",
        ),
        Index(
            "ix_security_events_tenant_event_type",
            "tenant_id",
            "event_type",
        ),
        Index(
            "ix_security_events_tenant_severity",
            "tenant_id",
            "severity",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<SecurityEvent "
            f"id={self.id} "
            f"tenant_id={self.tenant_id} "
            f"event_type={self.event_type} "
            f"severity={self.severity}>"
        )
