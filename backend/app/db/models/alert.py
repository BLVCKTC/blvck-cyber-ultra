from __future__ import annotations
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        CheckConstraint("severity IN ('info','low','medium','high','critical')", name="ck_alerts_severity"),
        CheckConstraint("status IN ('new','open','acknowledged','investigating','resolved','suppressed','false_positive')", name="ck_alerts_status"),
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="ck_alerts_risk_score"),
        UniqueConstraint("tenant_id", "fingerprint", name="uq_alerts_tenant_fingerprint"),
        Index("ix_alerts_tenant_status", "tenant_id", "status"),
        Index("ix_alerts_tenant_severity", "tenant_id", "severity"),
        Index("ix_alerts_tenant_updated", "tenant_id", "updated_at"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    detection_rule_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("detection_rules.id", ondelete="SET NULL"))
    security_event_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("security_events.id", ondelete="SET NULL"))
    fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'new'"))
    confidence: Mapped[int | None] = mapped_column(Integer)
    risk_score: Mapped[int | None] = mapped_column(Integer)
    source: Mapped[str | None] = mapped_column(String(255))
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
