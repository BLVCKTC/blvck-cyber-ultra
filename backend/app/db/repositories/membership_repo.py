from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, func, select, update
from sqlalchemy.orm import Session

from app.db.models.enums import MembershipRole
from app.db.models.membership import Membership
from app.db.models.tenant_role import TenantRole


class MembershipRepo:
    """
    Repository for tenant memberships.

    Responsibilities:
    - Retrieve memberships
    - Check membership existence
    - Create/update/delete memberships
    - Manage default tenant membership
    - Resolve tenant roles
    """

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # RETRIEVAL
    # =========================================================

    def get_by_id(self, membership_id: UUID) -> Membership | None:
        return self.db.get(Membership, membership_id)

    def get_membership(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> Membership | None:
        return self.db.scalar(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.tenant_id == tenant_id,
            )
        )

    def exists(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> bool:
        """Efficiently determine whether a user belongs to a tenant."""

        result = self.db.scalar(
            select(
                exists().where(
                    Membership.user_id == user_id,
                    Membership.tenant_id == tenant_id,
                )
            )
        )

        return bool(result)

    # =========================================================
    # USER MEMBERSHIPS
    # =========================================================

    def list_memberships_for_user(
        self,
        user_id: UUID,
    ) -> list[Membership]:
        """
        Return all tenant memberships belonging to a user.

        This is the canonical method used by AuthService.
        """

        return list(
            self.db.scalars(
                select(Membership)
                .where(Membership.user_id == user_id)
                .order_by(Membership.created_at)
            )
        )

    def list_for_user(
        self,
        user_id: UUID,
    ) -> list[Membership]:
        """
        Backwards-compatible alias for list_memberships_for_user().
        """

        return self.list_memberships_for_user(user_id)

    # =========================================================
    # TENANT MEMBERSHIPS
    # =========================================================

    def list_for_tenant(
        self,
        tenant_id: UUID,
    ) -> list[Membership]:
        return list(
            self.db.scalars(
                select(Membership)
                .where(Membership.tenant_id == tenant_id)
                .order_by(Membership.created_at)
            )
        )

    # =========================================================
    # ROLE / RBAC
    # =========================================================

    def count_by_role(
        self,
        tenant_id: UUID,
        role: MembershipRole,
    ) -> int:
        return (
            self.db.scalar(
                select(func.count())
                .select_from(Membership)
                .where(
                    Membership.tenant_id == tenant_id,
                    Membership.role == role,
                )
            )
            or 0
        )

    def get_tenant_role(
        self,
        tenant_id: UUID,
        role_key: str,
    ) -> TenantRole | None:
        return self.db.scalar(
            select(TenantRole).where(
                TenantRole.tenant_id == tenant_id,
                TenantRole.key == role_key,
            )
        )

    # =========================================================
    # PERSISTENCE
    # =========================================================

    def create(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
        role: MembershipRole,
        tenant_role_id: UUID | None = None,
        is_default: bool = False,
    ) -> Membership:
        """
        Create a tenant membership.

        If the new membership is marked as default,
        all other default memberships for the user are cleared.
        """

        if self.exists(user_id, tenant_id):
            raise ValueError(
                "User is already a member of this tenant."
            )

        if is_default:
            self.clear_default(user_id)

        membership = Membership(
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            tenant_role_id=tenant_role_id,
            is_default=is_default,
        )

        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)

        return membership

    def update_role(
        self,
        membership: Membership,
        role: MembershipRole,
    ) -> Membership:
        membership.role = role

        self.db.commit()
        self.db.refresh(membership)

        return membership

    def update_tenant_role(
        self,
        membership: Membership,
        tenant_role_id: UUID,
    ) -> Membership:
        membership.tenant_role_id = tenant_role_id

        self.db.commit()
        self.db.refresh(membership)

        return membership

    # =========================================================
    # DEFAULT TENANT MANAGEMENT
    # =========================================================

    def clear_default(
        self,
        user_id: UUID,
    ) -> None:
        """
        Remove default status from every membership belonging
        to the specified user.

        Does not commit so callers can include this operation
        in a larger transaction.
        """

        self.db.execute(
            update(Membership)
            .where(Membership.user_id == user_id)
            .values(is_default=False)
        )

    def set_default(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> None:
        """
        Set a user's active/default tenant.

        Only one membership can be the default tenant.
        """

        membership = self.get_membership(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        if membership is None:
            raise ValueError(
                "User is not a member of this tenant."
            )

        self.clear_default(user_id)

        self.db.execute(
            update(Membership)
            .where(
                Membership.user_id == user_id,
                Membership.tenant_id == tenant_id,
            )
            .values(is_default=True)
        )

        self.db.commit()

    # =========================================================
    # DELETION
    # =========================================================

    def delete(
        self,
        membership: Membership,
    ) -> None:
        self.db.delete(membership)
        self.db.commit()