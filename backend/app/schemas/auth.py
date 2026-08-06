from pydantic import BaseModel, Field

class TokenIntrospectionResult(BaseModel):
    sub: str
    email: str | None = None
    name: str | None = None
    roles: list[str] = Field(default_factory=list)

class UserOut(BaseModel):
    id: int
    email: str | None = None
    name: str | None = None

class TenantRoleOut(BaseModel):
    id: int | None = None
    key: str | None = None
    name: str | None = None

class MembershipOut(BaseModel):
    tenant_id: str
    role: str
    tenant_role: TenantRoleOut | None = None
    permissions: list[str] = Field(
        default_factory=list
    )

    is_default: bool

class MeResponse(BaseModel):
    user: UserOut
    memberships: list[MembershipOut]
    default_tenant_id: str | None = None
    permissions: list[str] = Field(default_factory=list)
class LoginResponse(BaseModel):
    authorization_url: str

class SetTenantResponse(BaseModel):
    ok: bool