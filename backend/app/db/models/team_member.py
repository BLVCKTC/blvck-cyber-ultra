from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import TeamMemberRole

if TYPE_CHECKING:
    from app.db.models.team import Team


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    team_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    membership_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("memberships.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[TeamMemberRole] = mapped_column(
        Enum(
            TeamMemberRole,
            name="teammemberrole",
        ),
        nullable=False,
        default=TeamMemberRole.MEMBER,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )

    team: Mapped[Team] = relationship(
        "Team",
        back_populates="members",
    )

    __table_args__ = (
        Index(
            "ix_team_member_team_membership",
            "team_id",
            "membership_id",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return (
            f"TeamMember(id={self.id!r}, "
            f"team_id={self.team_id!r}, "
            f"membership_id={self.membership_id!r}, "
            f"role={self.role.value!r})"
        )
