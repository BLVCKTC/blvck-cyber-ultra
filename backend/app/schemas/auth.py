from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field

class TokenIntrospectionResult(BaseModel):
    sub: str
    email: str | None = None
    name: str | None = None
    roles: list[str] = Field(default_factory=list)

class UserOut(BaseModel):
    id: UUID
    email: str | None = None
    name: str | None = None

class TenantRoleOut(BaseModel):
    id: UUID | None = None
    key: str | None = None
    name: str | None = None

class MembershipOut(BaseModel):
    tenant_id: UUID
    role: str
    tenant_role: TenantRoleOut | None = None
    permissions: list[str] = Field(default_factory=list)
    is_default: bool

class MeResponse(BaseModel):
    user: UserOut
    memberships: list[MembershipOut]
    default_tenant_id: UUID | None = None
    permissions: list[str] = Field(default_factory=list)

class LoginResponse(BaseModel):
    authorization_url: str

class SetTenantResponse(BaseModel):
    ok: bool
