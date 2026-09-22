from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Index, func, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CanaryMatch(Base):
    """One match produced by evaluating a CANARY-status rule against
    live traffic. Never becomes a real Alert or DetectionMatch — canary
    rules are explicitly not live-armed. Accumulates for the whole
    canary period; the eventual promotion gate aggregates over these
    plus the rule's own BacktestMatch rows.
    """

    __tablename__ = "canary_matches"
    __table_args__ = (
        Index("ix_canary_matches_tenant_rule", "tenant_id", "detection_rule_id"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    detection_rule_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("detection_rules.id", ondelete="CASCADE"), nullable=False
    )
    group_key: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    event_ids: Mapped[list[UUID]] = mapped_column(
        ARRAY(PG_UUID(as_uuid=True)), nullable=False, server_default=text("'{}'")
    )
    matched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)