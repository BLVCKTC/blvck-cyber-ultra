from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.db.models.enums import MembershipRole
from app.db.models.membership import Membership
from app.db.models.tenant_role import TenantRole


class MembershipRepo:
    """
    Repository for tenant memberships.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    # ---------------------------------------------------------
    # Get by ID
    # ---------------------------------------------------------

    def get_by_id(
        self,
        membership_id: int,
    ) -> Membership | None:

        return self.db.get(
            Membership,
            membership_id,
        )

    # ---------------------------------------------------------
    # Get membership
    # ---------------------------------------------------------

    def get_membership(
        self,
        user_id: int,
        tenant_id: str,
    ) -> Membership | None:

        return self.db.scalar(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.tenant_id == tenant_id,
            )
        )

    # ---------------------------------------------------------
    # Exists
    # ---------------------------------------------------------

    def exists(
        self,
        user_id: int,
        tenant_id: str,
    ) -> bool:

        return (
            self.get_membership(
                user_id,
                tenant_id,
            )
            is not None
        )

    # ---------------------------------------------------------
    # List memberships
    # ---------------------------------------------------------

    def list_for_user(
        self,
        user_id: int,
    ) -> list[Membership]:

        return list(
            self.db.scalars(
                select(Membership)
                .where(
                    Membership.user_id == user_id
                )
                .order_by(
                    Membership.created_at
                )
            ).all()
        )

    def list_memberships_for_user(
        self,
        user_id: int,
    ) -> list[Membership]:

        return self.list_for_user(user_id)

    # ---------------------------------------------------------
    # List tenant members
    # ---------------------------------------------------------

    def list_for_tenant(
        self,
        tenant_id: str,
    ) -> list[Membership]:

        return list(
            self.db.scalars(
                select(Membership)
                .where(
                    Membership.tenant_id == tenant_id
                )
                .order_by(
                    Membership.created_at
                )
            ).all()
        )

    # ---------------------------------------------------------
    # Count by legacy role
    # ---------------------------------------------------------

    def count_by_role(
        self,
        tenant_id: str,
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

    # ---------------------------------------------------------
    # Tenant Role lookup
    # ---------------------------------------------------------

    def get_tenant_role(
        self,
        tenant_id: str,
        role_key: str,
    ) -> TenantRole | None:

        return self.db.scalar(
            select(TenantRole).where(
                TenantRole.tenant_id == tenant_id,
                TenantRole.key == role_key,
            )
        )

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def create(
        self,
        *,
        user_id: int,
        tenant_id: str,
        role: MembershipRole,
        tenant_role_id: int | None = None,
        is_default: bool = False,
    ) -> Membership:

        if self.exists(
            user_id,
            tenant_id,
        ):
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

    # ---------------------------------------------------------
    # Update legacy role
    # ---------------------------------------------------------

    def update_role(
        self,
        membership: Membership,
        role: MembershipRole,
    ) -> Membership:

        membership.role = role

        self.db.commit()
        self.db.refresh(membership)

        return membership

    # ---------------------------------------------------------
    # Update tenant role
    # ---------------------------------------------------------

    def update_tenant_role(
        self,
        membership: Membership,
        tenant_role_id: int,
    ) -> Membership:

        membership.tenant_role_id = tenant_role_id

        self.db.commit()
        self.db.refresh(membership)

        return membership

    # ---------------------------------------------------------
    # Clear default
    # ---------------------------------------------------------

    def clear_default(
        self,
        user_id: int,
    ) -> None:

        self.db.execute(
            update(Membership)
            .where(
                Membership.user_id == user_id
            )
            .values(
                is_default=False
            )
        )

    # ---------------------------------------------------------
    # Set default tenant
    # ---------------------------------------------------------

    def set_default(
        self,
        user_id: int,
        tenant_id: str,
    ) -> None:

        self.clear_default(user_id)

        self.db.execute(
            update(Membership)
            .where(
                Membership.user_id == user_id,
                Membership.tenant_id == tenant_id,
            )
            .values(
                is_default=True
            )
        )

        self.db.commit()

    # Backwards compatibility
    def set_default_tenant(
        self,
        user_id: int,
        tenant_id: str,
    ) -> None:

        self.set_default(
            user_id,
            tenant_id,
        )

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete(
        self,
        membership: Membership,
    ) -> None:

        self.db.delete(membership)
        self.db.commit()