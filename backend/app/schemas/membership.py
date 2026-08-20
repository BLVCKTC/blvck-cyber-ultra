from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.db.models.enums import MembershipRole


class MembershipUser(BaseModel):
    id: UUID
    email: EmailStr | None = None
    name: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class MembershipCreate(BaseModel):
    """Add an existing user to a tenant."""
    user_id: UUID
    role: MembershipRole = MembershipRole.VIEWER
    is_default: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
    )


class MembershipUpdate(BaseModel):
    """Update an existing membership."""
    role: MembershipRole | None = None
    is_default: bool | None = None

    model_config = ConfigDict(
        populate_by_name=True,
    )


class MembershipResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    role: MembershipRole
    is_default: bool
    created_at: datetime
    updated_at: datetime
    user: MembershipUser

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class MembershipListResponse(BaseModel):
    items: list[MembershipResponse]
    total: int = Field(..., ge=0)

    model_config = ConfigDict(
        populate_by_name=True,
    )
