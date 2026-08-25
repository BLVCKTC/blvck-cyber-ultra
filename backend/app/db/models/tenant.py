from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.tenant_role import TenantRole

if TYPE_CHECKING:
    from app.db.models.membership import Membership


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # Profile
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(150), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status & Subscription
    plan: Mapped[str] = mapped_column(String(50), nullable=False, server_default="Free")
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="Active")

    # Security Posture
    security_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    features: Mapped[list[str]] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list, 
        server_default="[]"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), 
        nullable=False, 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )

    memberships: Mapped[list["Membership"]] = relationship(
        "Membership", 
        back_populates="tenant", 
        cascade="all, delete-orphan", 
        passive_deletes=True
    )
    roles: Mapped[list["TenantRole"]] = relationship(
        "TenantRole", 
        back_populates="tenant", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Tenant(id={self.id!r}, name={self.name!r}, slug={self.slug!r})"
