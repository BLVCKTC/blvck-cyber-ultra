from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.db.models.enums import MembershipRole

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.tenant import Tenant
    from app.db.models.tenant_role import TenantRole


class Membership(Base):

    __tablename__ = "memberships"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
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

    tenant_role_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "tenant_roles.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    role: Mapped[MembershipRole] = mapped_column(
        Enum(
            MembershipRole,
            name="membershiprole",
        ),
        nullable=False,
        default=MembershipRole.VIEWER,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
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

    user: Mapped["User"] = relationship(
        "User",
        back_populates="memberships",
        passive_deletes=True,
    )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="memberships",
        passive_deletes=True,
    )

    tenant_role: Mapped["TenantRole | None"] = relationship(
        "TenantRole",
        back_populates="memberships",
        lazy="joined",
    )

    __table_args__ = (
        Index(
            "ix_membership_user_tenant",
            "user_id",
            "tenant_id",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return (
            f"Membership("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"tenant_id={self.tenant_id}, "
            f"role={self.role.value}, "
            f"tenant_role_id={self.tenant_role_id}"
            f")"
        )