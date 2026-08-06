from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.role_permission import RolePermission
    from app.db.models.tenant_role_permission import TenantRolePermission


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    key: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    risk_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    tenant_role_permissions: Mapped[list["TenantRolePermission"]] = relationship(
        "TenantRolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
        passive_deletes=True,
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

    def __repr__(self) -> str:
        return (
            f"Permission("
            f"id={self.id}, "
            f"key={self.key!r}"
            f")"
        )