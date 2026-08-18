from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


if TYPE_CHECKING:
    from app.db.models.membership import Membership


class User(Base):

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    keycloak_sub: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    memberships: Mapped[list["Membership"]] = relationship(
        "Membership",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"User("
            f"id={self.id}, "
            f"email={self.email!r}, "
            f"keycloak_sub={self.keycloak_sub!r}"
            f")"
        )