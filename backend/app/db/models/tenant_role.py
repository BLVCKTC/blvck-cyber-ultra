from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.tenant import Tenant
    from app.db.models.membership import Membership
    from app.db.models.tenant_role_permission import TenantRolePermission


class TenantRole(Base):

    __tablename__ = "tenant_roles"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "key",
            name="uq_tenant_role_key",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "tenants.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="roles",
    )

    memberships: Mapped[list["Membership"]] = relationship(
        "Membership",
        back_populates="tenant_role",
    )

    permissions: Mapped[list["TenantRolePermission"]] = relationship(
        "TenantRolePermission",
        back_populates="tenant_role",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"TenantRole("
            f"id={self.id}, "
            f"key={self.key!r}"
            f")"
        )