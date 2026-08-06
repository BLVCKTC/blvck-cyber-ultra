from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.permission import Permission


class RolePermission(Base):
    """
    Global system role -> permission mapping.

    Examples
    --------
    OWNER -> platform.all
    ADMIN -> alerts.view
    ADMIN -> alerts.close
    SOC_ANALYST -> incidents.view

    These are the default templates used to seed
    tenant-specific roles.
    """

    __tablename__ = "role_permissions"

    role_key: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    permission_id: Mapped[int] = mapped_column(
        ForeignKey(
            "permissions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="role_permissions",
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "ix_role_permissions_role",
            "role_key",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"RolePermission("
            f"role_key={self.role_key!r}, "
            f"permission_id={self.permission_id}"
            f")"
        )