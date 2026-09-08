from __future__ import annotations
from uuid import UUID, uuid4
from sqlalchemy import String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    limits: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))