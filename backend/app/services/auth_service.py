from __future__ import annotations

from typing import Any

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


class AuthService:
    """
    Notes:
    - Keycloak authenticates the user (OIDC/OAuth2 + PKCE).
    - FastAPI manages application source-of-truth for:
      users, tenants/memberships, tenant roles, permissions, and session responses.
    """

    # If you want dynamic tenant selection from claims later, you can evolve this.
    # For now this keeps behavior aligned with your current implementation.
    TENANT_ID = "BLVCK-CYBER"

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepo(db)
        self.membership_repo = MembershipRepo(db)
        self.pkce = PKCEService(db)
        self.token_service = TokenService()

    def start_login(self, tenant_id: str) -> dict[str, str]:
        return self.pkce.create_login_request(tenant_id)

    async def exchange_code(
        self,
        *,
        code: str,
        attempt_id: str,
    ) -> dict[str, Any]:
        attempt = self.pkce.consume_attempt(attempt_id)

        token_response = await self.token_service.exchange_authorization_code(
            code=code,
            code_verifier=attempt["code_verifier"],
        )

        access_token = token_response.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="missing_access_token",
            )

        claims = verify_keycloak_access_token(access_token)

        # Verify ID token if present (your TokenService already supports it)
        await self.token_service.verify_id_token(
            token_response.get("id_token"),
            access_token,
        )

        user = self.get_or_create_user(claims)

        default = self.get_default_membership(user.id)

        # Keep your existing exchange_code response shape
        return {
            "access_token": access_token,
            "refresh_token": token_response.get("refresh_token"),
            "id_token": token_response.get("id_token"),
            "expires_in": token_response.get("expires_in"),
            "refresh_expires_in": token_response.get(
                "refresh_expires_in"
            ),
            "token_type": token_response.get(
                "token_type",
                "Bearer",
            ),
            "user": user,
            "default_tenant_id": (
                default.tenant_id
                if default
                else None
            ),
        }

    async def refresh_session(
        self,
        refresh_token: str,
    ) -> dict[str, Any]:
        """
        Refresh a Keycloak session using a refresh token.

        This method:
        - exchanges refresh token for new access token (+ possibly new refresh token)
        - verifies the new JWT
        - syncs the local user
        - syncs tenant memberships/roles
        - returns everything needed by the auth router (complete session object)
        """

        token_response = await self.token_service.refresh_access_token(
            refresh_token
        )

        access_token = token_response.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="unable_to_refresh_token",
            )

        # Verify JWT signature + claims and get normalized claims payload
        claims = verify_keycloak_access_token(access_token)

        # Verify the ID token if present (optional but recommended to keep parity)
        id_token = token_response.get("id_token")
        if id_token:
            await self.token_service.verify_id_token(
                id_token,
                access_token,
            )

        # Upsert user + sync membership role/tenant role mapping
        user = self.get_or_create_user(claims)

        default = self.get_default_membership(user.id)

        return {
            "access_token": access_token,
            "refresh_token": token_response.get(
                "refresh_token",
                refresh_token,  # fallback to old one if Keycloak doesn't rotate
            ),
            "id_token": id_token,
            "expires_in": token_response.get("expires_in"),
            "refresh_expires_in": token_response.get(
                "refresh_expires_in"
            ),
            "token_type": token_response.get(
                "token_type",
                "Bearer",
            ),
            "user": user,
            "default_tenant_id": (
                default.tenant_id
                if default
                else None
            ),
        }

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> dict[str, Any]:
        """
        Backwards-compatible wrapper.
        Avoids duplicated refresh logic by delegating to refresh_session().
        """
        return await self.refresh_session(refresh_token)

    def get_or_create_user(
        self,
        claims: dict[str, Any],
    ):
        keycloak_sub = claims.get("sub")
        if not keycloak_sub:
            raise HTTPException(
                status_code=400,
                detail="missing_subject_claim",
            )

        email = claims.get("email")
        name = (
            claims.get("name")
            or claims.get("preferred_username")
        )

        user = self.user_repo.upsert_from_token(
            keycloak_sub=keycloak_sub,
            email=email,
            name=name,
        )

        # IMPORTANT: this is where membership + tenant role are synced
        # based on Keycloak role claims.
        self.sync_keycloak_role(
            user.id,
            claims,
        )

        return user

    def extract_keycloak_role(
        self,
        claims: dict[str, Any],
    ) -> str:
        roles = claims.get(
            "realm_access",
            {},
        ).get(
            "roles",
            [],
        )

        supported_roles = {
            "OWNER",
            "ADMIN",
            "SOC_MANAGER",
            "SOC_ANALYST",
            "INCIDENT_RESPONDER",
            "VIEWER",
        }

        for role in roles:
            if role.upper() in supported_roles:
                return role.upper()

        return "VIEWER"

    def map_membership_role(
        self,
        role_key: str,
    ):
        # Keep your MembershipRole mapping centralized.
        mapping = {
            "OWNER": MembershipRole.OWNER,
            "ADMIN": MembershipRole.ADMIN,
            "SOC_MANAGER": MembershipRole.SOC_MANAGER,
            "SOC_ANALYST": MembershipRole.SOC_ANALYST,
            "INCIDENT_RESPONDER": MembershipRole.INCIDENT_RESPONDER,
            "VIEWER": MembershipRole.VIEWER,
        }

        return mapping.get(
            role_key,
            MembershipRole.VIEWER,
        )

    def sync_keycloak_role(
        self,
        user_id: int,
        claims: dict[str, Any],
    ):
        role_key = self.extract_keycloak_role(claims)
        legacy_role = self.map_membership_role(role_key)

        tenant_role = self.membership_repo.get_tenant_role(
            tenant_id=self.TENANT_ID,
            role_key=role_key,
        )
        if tenant_role is None:
            raise HTTPException(
                status_code=500,
                detail=f"Tenant role '{role_key}' does not exist",
            )

        membership = self.membership_repo.get_membership(
            user_id=user_id,
            tenant_id=self.TENANT_ID,
        )

        if membership:
            membership.role = legacy_role
            membership.tenant_role_id = tenant_role.id
            membership.is_default = True

            self.db.commit()
            self.db.refresh(membership)

        else:
            self.membership_repo.create(
                user_id=user_id,
                tenant_id=self.TENANT_ID,
                role=legacy_role,
                tenant_role_id=tenant_role.id,
                is_default=True,
            )

    def get_memberships(
        self,
        user_id: int,
    ):
        return self.membership_repo.list_memberships_for_user(
            user_id
        )

    def get_default_membership(
        self,
        user_id: int,
    ):
        memberships = self.get_memberships(user_id)
        if not memberships:
            return None

        return next(
            (
                membership
                for membership in memberships
                if membership.is_default
            ),
            memberships[0],
        )

    def set_default_tenant(
        self,
        user_id: int,
        tenant_id: str,
    ):
        membership = self.membership_repo.get_membership(
            user_id,
            tenant_id,
        )
        if membership is None:
            raise HTTPException(
                status_code=403,
                detail="not_a_member",
            )

        self.membership_repo.set_default_tenant(
            user_id,
            tenant_id,
        )

    def get_user_permissions(
        self,
        user_id: int,
        tenant_id: str | None,
    ) -> list[str]:
        if not tenant_id:
            return []

        membership = (
            self.db.query(Membership)
            .options(
                joinedload(Membership.tenant_role)
                .joinedload(TenantRole.permissions)
                .joinedload(TenantRolePermission.permission)
            )
            .filter(
                Membership.user_id == user_id,
                Membership.tenant_id == tenant_id,
            )
            .first()
        )

        if not membership or not membership.tenant_role:
            return []

        return [
            permission.permission.key
            for permission in membership.tenant_role.permissions
            if permission.permission
        ]

    def serialize_permissions(
        self,
        membership,
    ) -> list[str]:
        if not membership.tenant_role:
            return []

        return [
            permission.permission.key
            for permission in membership.tenant_role.permissions
            if permission.permission
        ]

    def build_me_response(
        self,
        user,
    ):
        memberships = self.get_memberships(user.id)
        default = self.get_default_membership(user.id)

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
            },
            "memberships": [
                {
                    "tenant_id": membership.tenant_id,
                    "role": membership.role.value,
                    "tenant_role": {
                        "id": (
                            membership.tenant_role.id
                            if membership.tenant_role
                            else None
                        ),
                        "key": (
                            membership.tenant_role.key
                            if membership.tenant_role
                            else None
                        ),
                        "name": (
                            membership.tenant_role.name
                            if membership.tenant_role
                            else None
                        ),
                    },
                    "permissions": self.serialize_permissions(
                        membership
                    ),
                    "is_default": membership.is_default,
                }
                for membership in memberships
            ],
            "default_tenant_id": (
                default.tenant_id
                if default
                else None
            ),
        }

    def logout(self):
        return {"ok": True}
