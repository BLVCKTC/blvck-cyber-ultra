from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base  # adjust to your actual Base import


class QuarantinedEvent(Base):
    """
    Events that failed normalization or validation during ingestion.

    Stored so they can be inspected and, once the underlying bug or
    source-format issue is fixed, reprocessed through the pipeline rather
    than being lost on rejection.
    """

    __tablename__ = "quarantined_events"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(255), nullable=False)

    # Where in the pipeline it failed: "normalization" or "validation"
    failure_stage: Mapped[str] = mapped_column(String(32), nullable=False)

    failure_reason: Mapped[str] = mapped_column(Text, nullable=False)

    # The untouched original payload, exactly as received
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Best-effort partial normalization output, if it got that far — useful
    # for debugging without re-running the pipeline by hand
    partial_normalized: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    quarantined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index(
            "ix_quarantined_events_tenant_unresolved",
            "tenant_id",
            "resolved_at",
        ),
    )