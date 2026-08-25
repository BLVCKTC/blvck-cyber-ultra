from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class TokenIntrospectionResult(BaseModel):
    sub: str
    email: str | None = None
    name: str | None = None
    roles: list[str] = Field(default_factory=list)

class UserOut(BaseSchema):
    id: UUID
    email: str | None = None
    name: str | None = None

class TenantRoleOut(BaseSchema):
    id: UUID | None = None
    key: str | None = None
    name: str | None = None

class MembershipOut(BaseSchema):
    tenant_id: UUID
    tenant_name: str | None = None
    role: str
    tenant_role: TenantRoleOut | None = None
    permissions: list[str] = Field(default_factory=list)
    is_default: bool = False

class MeResponse(BaseSchema):
    user: UserOut
    memberships: list[MembershipOut] = Field(default_factory=list)
    default_tenant_id: UUID | None = None
    permissions: list[str] = Field(default_factory=list)

class LoginResponse(BaseModel):
    authorization_url: str

class SetTenantResponse(BaseModel):
    ok: bool
