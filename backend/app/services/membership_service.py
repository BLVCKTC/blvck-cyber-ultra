from __future__ import annotations

from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.enums import MembershipRole
from app.db.models.membership import Membership
from app.db.repositories.membership_repo import MembershipRepo
from app.db.repositories.user_repo import UserRepo
from app.schemas.membership import MembershipCreate, MembershipUpdate


class MembershipService:
    """Business logic for tenant memberships."""

    def __init__(self, db: Session):
        self.db = db
        self.memberships = MembershipRepo(db)
        self.users = UserRepo(db)

    def _get_required_user(self, user_id: UUID):
        user = self.users.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user_not_found")
        return user

    def _get_required_membership(self, membership_id: UUID) -> Membership:
        membership = self.memberships.get_by_id(membership_id)
        if membership is None:
            raise HTTPException(
                status_code=404,
                detail="membership_not_found",
            )
        return membership

    def _assert_not_last_owner(
        self,
        *,
        tenant_id: UUID,
        current_role: MembershipRole,
        next_role: MembershipRole | None,
    ) -> None:
        if current_role != MembershipRole.OWNER:
            return

        if next_role == MembershipRole.OWNER:
            return

        owner_count = self.memberships.count_by_role(tenant_id, MembershipRole.OWNER)
        if owner_count == 1:
            if next_role is None:
                raise HTTPException(status_code=400, detail="cannot_remove_last_owner")
            raise HTTPException(status_code=400, detail="cannot_demote_last_owner")

    def list_members(self, tenant_id: UUID) -> list[Membership]:
        return self.memberships.list_for_tenant(tenant_id)

    def get(self, membership_id: UUID) -> Membership:
        return self._get_required_membership(membership_id)

    def add_member(self, tenant_id: UUID, payload: MembershipCreate) -> Membership:
        self._get_required_user(payload.user_id)

        if self.memberships.exists(payload.user_id, tenant_id):
            raise HTTPException(status_code=409, detail="user_already_member")

        try:
            return self.memberships.create(
                user_id=payload.user_id,
                tenant_id=tenant_id,
                role=payload.role,
                is_default=payload.is_default,
            )
        except ValueError:
            raise HTTPException(status_code=409, detail="user_already_member")

    def update_member(self, membership_id: UUID, payload: MembershipUpdate) -> Membership:
        membership = self._get_required_membership(membership_id)

        if payload.role is not None:
            self._assert_not_last_owner(
                tenant_id=membership.tenant_id,
                current_role=membership.role,
                next_role=payload.role,
            )
            membership = self.memberships.update_role(
                membership=membership,
                role=payload.role,
            )

        if payload.is_default is True:
            self.memberships.set_default(
                user_id=membership.user_id,
                tenant_id=membership.tenant_id,
            )
            membership = self._get_required_membership(membership_id)

        return membership

    def remove_member(self, membership_id: UUID) -> None:
        membership = self._get_required_membership(membership_id)

        self._assert_not_last_owner(
            tenant_id=membership.tenant_id,
            current_role=membership.role,
            next_role=None,
        )

        self.memberships.delete(membership)
