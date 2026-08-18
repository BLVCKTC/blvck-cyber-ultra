from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


if TYPE_CHECKING:
    from app.db.models.tenant import Tenant


class PKCEAttempt(Base):

    __tablename__ = "pkce_attempts"

    attempt_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "tenants.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    code_verifier: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )