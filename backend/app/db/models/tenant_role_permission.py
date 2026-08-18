from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.permission import Permission
    from app.db.models.tenant_role import TenantRole


class TenantRolePermission(Base):

    __tablename__ = "tenant_role_permissions"

    __table_args__ = (
        UniqueConstraint(
            "tenant_role_id",
            "permission_id",
            name="uq_role_permission",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    tenant_role_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "tenant_roles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    permission_id: Mapped[int] = mapped_column(
        ForeignKey(
            "permissions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    tenant_role: Mapped["TenantRole"] = relationship(
        "TenantRole",
        back_populates="permissions",
        passive_deletes=True,
    )

    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="tenant_role_permissions",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"TenantRolePermission("
            f"tenant_role_id={self.tenant_role_id}, "
            f"permission_id={self.permission_id}"
            f")"
        )