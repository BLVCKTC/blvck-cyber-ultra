from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PKCEAttempt(Base):
    __tablename__ = "pkce_attempts"

    attempt_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    tenant_id: Mapped[str] = mapped_column(
        String(64),
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