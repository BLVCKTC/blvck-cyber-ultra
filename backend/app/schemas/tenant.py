from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class TenantBase(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    slug: str | None = Field(default=None, min_length=2, max_length=255)
    website: str | None = Field(default=None, max_length=500)
    email: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=150)
    location: str | None = Field(default=None, max_length=255)
    plan: str | None = Field(default=None, max_length=50)
    status: str | None = Field(default=None, max_length=50)
    security_score: int | None = Field(default=None, ge=0, le=100)
    features: list[str] = Field(default_factory=list)


class TenantCreate(TenantBase):
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=255)


class TenantUpdate(TenantBase):
    features: list[str] | None = Field(default=None)


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    name: str
    slug: str
    website: str | None = None
    email: str | None = None
    industry: str | None = None
    location: str | None = None
    plan: str
    status: str
    security_score: int | None = Field(
        default=None,
        validation_alias=AliasChoices("security_score", "securityScore"),
        serialization_alias="securityScore",
    )
    features: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class TenantListResponse(BaseModel):
    items: list[TenantResponse]


class SetTenantIn(BaseModel):
    tenant_id: UUID
