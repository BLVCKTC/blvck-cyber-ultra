from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.tenant_role import TenantRole

if TYPE_CHECKING:
    from app.db.models.membership import Membership


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    memberships: Mapped[list["Membership"]] = relationship(
        "Membership",
        back_populates="tenant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    roles: Mapped[list["TenantRole"]] = relationship(
    "TenantRole",
    back_populates="tenant",
    cascade="all, delete-orphan",
) 

    def __repr__(self) -> str:
        return (
            f"Tenant("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"slug={self.slug!r}"
            f")"
        )
