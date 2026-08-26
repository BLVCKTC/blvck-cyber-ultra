from __future__ import annotations
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Investigation(Base):
    __tablename__ = 'investigations'
    __table_args__ = (Index('ix_investigations_tenant_status', 'tenant_id', 'status'), Index('ix_investigations_tenant_updated', 'tenant_id', 'updated_at'))
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    alert_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('alerts.id', ondelete='SET NULL'))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'open'"))
    assignee_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

class Evidence(Base):
    __tablename__ = 'evidence'
    __table_args__ = (Index('ix_evidence_tenant_investigation', 'tenant_id', 'investigation_id'), Index('ix_evidence_tenant_created', 'tenant_id', 'created_at'))
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    investigation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('investigations.id', ondelete='CASCADE'), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(512))
    notes: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
