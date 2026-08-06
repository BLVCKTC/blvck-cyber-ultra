from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.db.models.enums import MembershipRole


class MembershipUser(BaseModel):
    id: int
    email: EmailStr | None = None
    name: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

class MembershipCreate(BaseModel):
    """
    Add an existing user to a tenant.
    """

    user_id: int = Field(..., gt=0)
    role: MembershipRole = MembershipRole.VIEWER
    is_default: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
    )


class MembershipUpdate(BaseModel):
    """
    Update an existing membership.
    All fields are optional; when omitted they are not changed.
    """

    role: MembershipRole | None = None
    is_default: bool | None = None

    model_config = ConfigDict(
        populate_by_name=True,
    )

class MembershipResponse(BaseModel):
    id: int = Field(..., gt=0)
    tenant_id: str = Field(..., min_length=1)
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
