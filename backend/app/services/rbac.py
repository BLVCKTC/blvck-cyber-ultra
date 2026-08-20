from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.membership import Membership
from app.db.models.permission import Permission
from app.db.models.tenant_role_permission import TenantRolePermission


class RBACService:
    """
    Database-backed RBAC service.

    Permission resolution path:

    Membership
        ->
    TenantRole
        ->
    TenantRolePermission
        ->
    Permission
    """

    SUPER_PERMISSION = "platform.all"

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # Membership
    # ---------------------------------------------------------

    def get_membership(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> Membership | None:

        return (
            self.db.query(Membership)
            .filter(
                Membership.user_id == user_id,
                Membership.tenant_id == tenant_id,
            )
            .first()
        )

    # ---------------------------------------------------------
    # Role
    # ---------------------------------------------------------

    def get_role(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> dict | None:

        membership = self.get_membership(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        if membership is None:
            return None

        if membership.tenant_role is None:
            return None

        role = membership.tenant_role

        return {
            "id": role.id,
            "key": role.key,
            "name": role.name,
            "is_system": role.is_system,
            "is_default": membership.is_default,
        }

    # ---------------------------------------------------------
    # Permissions
    # ---------------------------------------------------------

    def get_permissions(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> list[str]:

        membership = self.get_membership(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        if membership is None:
            return []

        if membership.tenant_role_id is None:
            return []

        rows = (
            self.db.query(Permission.key)
            .join(
                TenantRolePermission,
                TenantRolePermission.permission_id == Permission.id,
            )
            .filter(
                TenantRolePermission.tenant_role_id
                == membership.tenant_role_id
            )
            .order_by(Permission.key)
            .all()
        )

        return [row.key for row in rows]

    # ---------------------------------------------------------
    # Permission checks
    # ---------------------------------------------------------

    def has_permission(
        self,
        user_id: UUID,
        tenant_id: UUID,
        permission_key: str,
    ) -> bool:

        permissions = set(
            self.get_permissions(
                user_id=user_id,
                tenant_id=tenant_id,
            )
        )

        if self.SUPER_PERMISSION in permissions:
            return True

        return permission_key in permissions

    def has_any_permission(
        self,
        user_id: UUID,
        tenant_id: UUID,
        permission_keys: list[str],
    ) -> bool:

        permissions = set(
            self.get_permissions(
                user_id=user_id,
                tenant_id=tenant_id,
            )
        )

        if self.SUPER_PERMISSION in permissions:
            return True

        return any(
            permission in permissions
            for permission in permission_keys
        )

    def has_all_permissions(
        self,
        user_id: UUID,
        tenant_id: UUID,
        permission_keys: list[str],
    ) -> bool:

        permissions = set(
            self.get_permissions(
                user_id=user_id,
                tenant_id=tenant_id,
            )
        )

        if self.SUPER_PERMISSION in permissions:
            return True

        return all(
            permission in permissions
            for permission in permission_keys
        )

    # ---------------------------------------------------------
    # Complete authorization context
    # ---------------------------------------------------------

    def get_authorization_context(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> dict:

        role = self.get_role(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        permissions = self.get_permissions(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        return {
            "role": role,
            "permissions": permissions,
        }