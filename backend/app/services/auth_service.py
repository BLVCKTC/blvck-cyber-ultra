from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.security.jwt_verify import verify_keycloak_access_token
from app.db.models.enums import MembershipRole
from app.db.models.membership import Membership
from app.db.models.tenant_role import TenantRole
from app.db.models.tenant_role_permission import TenantRolePermission
from app.db.repositories.membership_repo import MembershipRepo
from app.db.repositories.user_repo import UserRepo
from app.services.pkce_service import PKCEService
from app.services.token_service import TokenService

# Centralized mapping to remove redundancy between extraction and mapping methods
ROLE_MAPPING = {
    "OWNER": MembershipRole.OWNER,
    "ADMIN": MembershipRole.ADMIN,
    "SOC_MANAGER": MembershipRole.SOC_MANAGER,
    "SOC_ANALYST": MembershipRole.SOC_ANALYST,
    "INCIDENT_RESPONDER": MembershipRole.INCIDENT_RESPONDER,
    "VIEWER": MembershipRole.VIEWER,
}

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepo(db)
        self.membership_repo = MembershipRepo(db)
        self.pkce = PKCEService(db)
        self.token_service = TokenService()

    def start_login(self, tenant_id: UUID | None = None) -> dict[str, str]:
        return self.pkce.create_login_request(tenant_id)

    async def _process_token_response(self, token_response: dict[str, Any], sync_roles: bool = False, tenant_id: UUID | None = None) -> tuple[dict[str, Any], Any]:
        """Internal helper to handle token verification and user retrieval for both login and refresh."""
        access_token = token_response.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="missing_access_token")

        claims = verify_keycloak_access_token(access_token)
        id_token = token_response.get("id_token")
        if id_token:
            await self.token_service.verify_id_token(id_token, access_token)

        user = self.get_or_create_user(claims=claims, tenant_id=tenant_id, sync_roles=sync_roles)
        return token_response, user

    async def exchange_code(self, *, code: str, attempt_id: str) -> dict[str, Any]:
        attempt = self.pkce.consume_attempt(attempt_id)
        tenant_id_raw = attempt.get("tenant_id")
        tenant_id = UUID(str(tenant_id_raw)) if tenant_id_raw else None

        token_response = await self.token_service.exchange_authorization_code(
            code=code, code_verifier=attempt["code_verifier"]
        )
        
        token_data, user = await self._process_token_response(token_response, sync_roles=True, tenant_id=tenant_id)

        membership = (
            self.membership_repo.get_membership(user_id=user.id, tenant_id=tenant_id)
            if tenant_id
            else None
        )
        default = self.get_default_membership(user.id)

        if tenant_id and not membership:
            raise HTTPException(status_code=403, detail="not_a_member")

        return {
            **token_data,
            "user": user,
            "tenant_id": membership.tenant_id if membership else None,
            "default_tenant_id": default.tenant_id if default else None,
            "token_type": token_data.get("token_type", "Bearer"),
        }

    async def refresh_session(self, refresh_token: str) -> dict[str, Any]:
        token_response = await self.token_service.refresh_access_token(refresh_token)
        token_data, user = await self._process_token_response(token_response)
        
        default = self.get_default_membership(user.id)

        return {
            **token_data,
            "refresh_token": token_data.get("refresh_token", refresh_token),
            "user": user,
            "default_tenant_id": default.tenant_id if default else None,
            "token_type": token_data.get("token_type", "Bearer"),
        }

    def get_or_create_user(self, *, claims: dict[str, Any], tenant_id: UUID | None = None, sync_roles: bool = False):
        keycloak_sub = claims.get("sub")
        if not keycloak_sub:
            raise HTTPException(status_code=400, detail="missing_subject_claim")

        user = self.user_repo.upsert_from_token(
            keycloak_sub=keycloak_sub,
            email=claims.get("email"),
            name=claims.get("name") or claims.get("preferred_username"),
        )

        if sync_roles and tenant_id:
            self.sync_keycloak_role(user_id=user.id, tenant_id=tenant_id, claims=claims)

        return user

    def sync_keycloak_role(self, *, user_id: UUID, tenant_id: UUID, claims: dict[str, Any]):
        # Extract and map role in one step using the constant map
        roles = (claims.get("realm_access") or {}).get("roles") or []
        role_key = next((r.upper() for r in roles if r.upper() in ROLE_MAPPING), "VIEWER")
        membership_role = ROLE_MAPPING[role_key]

        tenant_role = self.membership_repo.get_tenant_role(tenant_id=tenant_id, role_key=role_key)
        if not tenant_role:
            raise HTTPException(status_code=500, detail=f"Tenant role {role_key} not configured for tenant {tenant_id}")

        membership = self.membership_repo.get_membership(user_id=user_id, tenant_id=tenant_id)
        if membership:
            return membership

        return self.membership_repo.create(
            user_id=user_id, tenant_id=tenant_id, role=membership_role, tenant_role_id=tenant_role.id, is_default=False
        )

    def get_memberships(self, user_id: UUID):
        return self.membership_repo.list_memberships_for_user(user_id)

    def get_default_membership(self, user_id: UUID):
        memberships = self.get_memberships(user_id)
        if not memberships:
            return None
        return next((m for m in memberships if m.is_default), memberships[0])

    def set_default_tenant(self, user_id: UUID, tenant_id: UUID):
        if not self.membership_repo.get_membership(user_id, tenant_id):
            raise HTTPException(status_code=403, detail="not_a_member")
        self.membership_repo.set_default_tenant(user_id, tenant_id)

    def get_permissions(self, membership: Membership) -> list[str]:
        """Unified permission extraction used by both MeResponse and general lookups."""
        if not membership or not membership.tenant_role:
            return []
        return [p.permission.key for p in membership.tenant_role.permissions if p.permission]

    def get_user_permissions(self, user_id: UUID, tenant_id: UUID | None) -> list[str]:
        if not tenant_id:
            return []
        
        membership = (
            self.db.query(Membership)
            .options(joinedload(Membership.tenant_role).joinedload(TenantRole.permissions).joinedload(TenantRolePermission.permission))
            .filter(Membership.user_id == user_id, Membership.tenant_id == tenant_id)
            .first()
        )
        return self.get_permissions(membership)

    def build_me_response(self, user):
        # Optimization: Fetch memberships once and derive the default from that list
        memberships = self.get_memberships(user.id)
        default_membership = next((m for m in memberships if m.is_default), memberships[0] if memberships else None)

        return {
            "user": {"id": user.id, "email": user.email, "name": user.name},
            "memberships": [
                {
                    "tenant_id": m.tenant_id,
                    "role": m.role.value,
                    "tenant_role": {
                        "id": m.tenant_role.id if m.tenant_role else None,
                        "key": m.tenant_role.key if m.tenant_role else None,
                        "name": m.tenant_role.name if m.tenant_role else None,
                    },
                    "permissions": self.get_permissions(m),
                    "is_default": m.is_default,
                }
                for m in memberships
            ],
            "default_tenant_id": default_membership.tenant_id if default_membership else None,
        }

    def logout(self):
        return {"ok": True}
