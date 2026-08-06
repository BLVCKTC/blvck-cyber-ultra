from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=255,
    )

    slug: str = Field(
        min_length=2,
        max_length=255,
    )


class TenantUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime


class TenantListResponse(BaseModel):
    items: list[TenantResponse]


class SetTenantIn(BaseModel):
    tenant_id: str