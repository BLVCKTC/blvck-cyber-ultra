from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DetectionRuleType(enum.StrEnum):
    THRESHOLD = "threshold"
    QUERY = "query"
    CORRELATION = "correlation"
    BEHAVIORAL = "behavioral"
    SIGMA = "sigma"


class DetectionRuleSeverity(enum.StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionRuleStatus(enum.StrEnum):
    DRAFT = "draft"
    TESTING = "testing"
    BACKTESTED = "backtested"
    CANARY = "canary"
    APPROVED = "approved"
    PRODUCTION = "production"
    MONITORED = "monitored"
    TUNED = "tuned"
    RETIRED = "retired"


class DetectionRule(Base):
    __tablename__ = "detection_rules"
    __table_args__ = (
        CheckConstraint("version > 0", name="ck_detection_rules_version_positive"),
        CheckConstraint("rule_type IN ('threshold','query','correlation','behavioral','sigma')", name="ck_detection_rules_type"),
        CheckConstraint("severity IN ('info','low','medium','high','critical')", name="ck_detection_rules_severity"),
        CheckConstraint("status IN ('draft','testing','backtested','canary','approved','production','monitored','tuned','retired')", name="ck_detection_rules_status"),
        Index("ix_detection_rules_tenant_status", "tenant_id", "status"),
        Index("ix_detection_rules_tenant_enabled", "tenant_id", "enabled"),
        Index("ix_detection_rules_tenant_type", "tenant_id", "rule_type"),
        Index("ix_detection_rules_tenant_severity", "tenant_id", "severity"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    rule_type: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft", server_default=text("'draft'"))
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default=text("1"))
    enabled: Mapped[bool] = mapped_column(nullable=False, default=True, server_default=text("true"))
    query: Mapped[str | None] = mapped_column(Text)
    configuration: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(100)), nullable=False, default=list, server_default=text("'{}'"))
    mitre_technique_ids: Mapped[list[str]] = mapped_column(ARRAY(String(50)), nullable=False, default=list, server_default=text("'{}'"))
    mitre_tactic_ids: Mapped[list[str]] = mapped_column(ARRAY(String(50)), nullable=False, default=list, server_default=text("'{}'"))
    author: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def is_production_eligible(self) -> bool:
        return self.status == DetectionRuleStatus.PRODUCTION and self.enabled
