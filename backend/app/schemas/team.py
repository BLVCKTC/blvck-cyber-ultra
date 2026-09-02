from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.enums import TeamMemberRole


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class TeamUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class TeamResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TeamListResponse(BaseModel):
    items: list[TeamResponse]
    total: int = Field(..., ge=0)

    model_config = ConfigDict(populate_by_name=True)


class TeamMemberCreate(BaseModel):
    """Add an existing tenant member (by membership_id) to a team."""
    membership_id: UUID
    role: TeamMemberRole = TeamMemberRole.MEMBER

    model_config = ConfigDict(populate_by_name=True)


class TeamMemberUpdate(BaseModel):
    role: TeamMemberRole

    model_config = ConfigDict(populate_by_name=True)


class TeamMemberResponse(BaseModel):
    id: UUID
    team_id: UUID
    membership_id: UUID
    role: TeamMemberRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TeamMemberListResponse(BaseModel):
    items: list[TeamMemberResponse]
    total: int = Field(..., ge=0)

    model_config = ConfigDict(populate_by_name=True)