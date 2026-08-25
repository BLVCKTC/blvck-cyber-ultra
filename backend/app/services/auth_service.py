from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security.jwt_verify import verify_keycloak_access_token
from app.db.models.enums import MembershipRole
from app.db.models.membership import Membership
from app.db.repositories.membership_repo import MembershipRepo
from app.db.repositories.user_repo import UserRepo
from app.schemas.auth import MeResponse, MembershipOut, UserOut
from app.services.pkce_service import PKCEService
from app.services.token_service import TokenService


ROLE_MAPPING: dict[str, MembershipRole] = {
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

    async def _process_token_response(self, token_response: dict[str, Any]) -> tuple[dict[str, Any], Any, dict[str, Any]]:
        access_token = token_response.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="missing_access_token")

        claims = verify_keycloak_access_token(access_token)

        id_token = token_response.get("id_token")
        if id_token:
            await self.token_service.verify_id_token(id_token, access_token)

        user = self.get_or_create_user(claims=claims)
        return token_response, user, claims

    async def exchange_code(self, *, code: str, attempt_id: str) -> dict[str, Any]:
        attempt = self.pkce.consume_attempt(attempt_id)
        tenant_id = attempt.get("tenant_id")

        token_response = await self.token_service.exchange_authorization_code(
            code=code, 
            code_verifier=attempt["code_verifier"]
        )

        token_data, user, claims = await self._process_token_response(token_response)

        membership = None
        if tenant_id:
            membership = self.membership_repo.get_membership(user_id=user.id, tenant_id=tenant_id)
            if not membership:
                raise HTTPException(status_code=403, detail="not_a_member")
            
            membership = self.sync_keycloak_role(user_id=user.id, tenant_id=tenant_id, claims=claims)

        if not membership:
            membership = self.get_default_membership(user.id)

        return {
            **token_data,
            "user": user,
            "tenant_id": membership.tenant_id if membership else None,
            "default_tenant_id": membership.tenant_id if membership else None,
            "token_type": token_data.get("token_type", "Bearer"),
        }

    async def refresh_session(self, refresh_token: str) -> dict[str, Any]:
        token_response = await self.token_service.refresh_access_token(refresh_token)
        token_data, user, _ = await self._process_token_response(token_response)
        
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

    def sync_keycloak_role(self, *, user_id: UUID, tenant_id: UUID, claims: dict[str, Any]) -> Membership:
        roles = (claims.get("realm_access") or {}).get("roles") or []
        normalized_roles = {str(role).upper() for role in roles}
        
        role_key = next((role for role in normalized_roles if role in ROLE_MAPPING), "VIEWER")
        membership_role = ROLE_MAPPING[role_key]

        tenant_role = self.membership_repo.get_tenant_role(tenant_id=tenant_id, role_key=role_key)
        if not tenant_role:
            raise HTTPException(status_code=500, detail=f"Role {role_key} not configured for tenant {tenant_id}")

        membership = self.membership_repo.get_membership(user_id=user_id, tenant_id=tenant_id)

        if membership:
            if membership.role != membership_role or membership.tenant_role_id != tenant_role.id:
                membership = self.membership_repo.update_membership_role(
                    membership=membership, 
                    role=membership_role, 
                    tenant_role_id=tenant_role.id
                )
            return membership

        return self.membership_repo.create(
            user_id=user_id,
            tenant_id=tenant_id,
            role=membership_role,
            tenant_role_id=tenant_role.id,
            is_default=False,
        )

    def get_memberships(self, user_id: UUID) -> list[Membership]:
        return self.membership_repo.list_for_user(user_id)

    def get_default_membership(self, user_id: UUID) -> Membership | None:
        memberships = self.get_memberships(user_id)
        if not memberships:
            return None
        return next((m for m in memberships if m.is_default), memberships[0])

    def set_default_tenant(self, user_id: UUID, tenant_id: UUID) -> None:
        if not self.membership_repo.get_membership(user_id=user_id, tenant_id=tenant_id):
            raise HTTPException(status_code=403, detail="not_a_member")
        
        self.membership_repo.set_default(user_id=user_id, tenant_id=tenant_id)

    def get_permissions(self, membership: Membership | None) -> list[str]:
        if not membership or not membership.tenant_role:
            return []
        return [p.permission.key for p in membership.tenant_role.permissions if p.permission]

    def get_user_permissions(self, user_id: UUID, tenant_id: UUID | None) -> list[str]:
        if not tenant_id:
            return []
        return self.get_permissions(self.membership_repo.get_membership(user_id=user_id, tenant_id=tenant_id))

    def build_me_response(self, user: Any) -> dict[str, Any]:
        memberships = self.get_memberships(user.id)
        default = next((m for m in memberships if m.is_default), memberships[0] if memberships else None)

        membership_data = [
            MembershipOut(
                tenant_id=m.tenant_id,
                tenant_name= m.tenant.name if m.tenant is not None else None ,
                role=m.role.value if hasattr(m.role, "value") else str(m.role),
                tenant_role=m.tenant_role,
                permissions=self.get_permissions(m),
                is_default=bool(m.is_default),
            )
            for m in memberships
        ]

        return MeResponse(
            user=UserOut.model_validate(user),
            memberships=membership_data,
            default_tenant_id=default.tenant_id if default else None,
            permissions=self.get_permissions(default),
        ).model_dump()

    def logout(self) -> dict[str, bool]:
        return {"ok": True}
