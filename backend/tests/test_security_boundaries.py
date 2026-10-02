"""
Security-boundary test suite (Recommendation #6).

These tests exercise the authorization seams that live in
``app.api.deps`` *directly* — no live Keycloak server and no Postgres
connection. The dependency callables are invoked with fake users /
memberships, and their data-access collaborators (``MembershipRepo``,
``RBACService``) are monkeypatched onto the ``app.api.deps`` module so the
boundary logic is asserted in isolation.

Coverage:

1. Tenant isolation  -> ``get_active_membership``
     A user must NOT reach a tenant they are not a member of, even with a
     valid session and an arbitrary ``tenant_id`` cookie.

2. Permission denial -> ``require_permission`` / ``require_roles``
     A member without the required RBAC permission (or legacy role) is
     rejected with 403; a member with it (or the ``platform.all`` super
     permission) passes.

3. AI-cannot-execute -> covered in ``tests/test_agent_authority_boundary.py``
     The agent layer now exists. Its authority boundary (agent import
     allowlist, dynamic-import ban, the human auth chain on the orchestrate
     route, and the write-scope check that a real run changes only the
     investigations and evidence tables) is asserted there, not here.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)
from uuid import uuid4
from app.db.models.enums import MembershipRole

from tests.conftest import (
    FakeMembership,
    FakeRequest,
    make_membership_repo,
    make_rbac_service,
)


# ======================================================================
# 1. TENANT ISOLATION  (get_active_membership)
# ======================================================================

class TestTenantIsolation:
    """
    ``get_active_membership`` is the single seam that enforces tenancy. It
    reads the tenant ID from the request and looks up a membership for
    ``(user.id, tenant_id)``. If none exists the request is rejected with 403.
    """

    def test_cross_tenant_access_is_denied(
        self, deps_module, fake_user, fake_db, monkeypatch
    ):
        tenant_id = uuid4()

        monkeypatch.setattr(
            deps_module,
            "MembershipRepo",
            make_membership_repo(None),
        )

        request = FakeRequest(
            {
                deps_module.ACTIVE_TENANT_COOKIE_NAME: str(tenant_id),
            }
        )

        with pytest.raises(HTTPException) as exc_info:
            deps_module.get_active_membership(
                request=request,
                db=fake_db,
                user=fake_user,
            )

        assert exc_info.value.status_code == HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "not_a_member"

    def test_same_tenant_member_is_allowed(
        self, deps_module, fake_user, fake_db, monkeypatch
    ):
        tenant_id = uuid4()

        membership = FakeMembership(
            user_id=fake_user.id,
            tenant_id=tenant_id,
        )

        monkeypatch.setattr(
            deps_module,
            "MembershipRepo",
            make_membership_repo(membership),
        )

        request = FakeRequest(
            {
                deps_module.ACTIVE_TENANT_COOKIE_NAME: str(tenant_id),
            }
        )

        result = deps_module.get_active_membership(
            request=request,
            db=fake_db,
            user=fake_user,
        )

        assert result is membership
        assert result.tenant_id == tenant_id

    def test_missing_tenant_cookie_is_denied(
        self, deps_module, fake_user, fake_db, monkeypatch
    ):
        monkeypatch.setattr(
            deps_module,
            "MembershipRepo",
            make_membership_repo(FakeMembership()),
        )

        request = FakeRequest({})

        with pytest.raises(HTTPException) as exc_info:
            deps_module.get_active_membership(
                request=request,
                db=fake_db,
                user=fake_user,
            )

        assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "tenant_not_selected"


# ======================================================================
# 2a. PERMISSION DENIAL  (require_permission -> RBACService)
# ======================================================================

class TestRequirePermission:
    """
    ``require_permission(key)`` builds an RBACService and calls
    ``has_permission``. A False result must raise 403 with a structured
    ``permission_denied`` payload naming the required permission.
    """

    def test_permission_denied_returns_403(
        self, deps_module, fake_membership, fake_db, monkeypatch
    ):
        monkeypatch.setattr(
            deps_module,
            "RBACService",
            make_rbac_service(allow=False),
        )

        dependency = deps_module.require_permission("alerts.view")

        with pytest.raises(HTTPException) as exc_info:
            dependency(membership=fake_membership, db=fake_db)

        assert exc_info.value.status_code == HTTP_403_FORBIDDEN
        assert exc_info.value.detail["error"] == "permission_denied"
        assert exc_info.value.detail["required_permission"] == "alerts.view"

    def test_permission_granted_returns_membership(
        self, deps_module, fake_membership, fake_db, monkeypatch
    ):
        monkeypatch.setattr(
            deps_module,
            "RBACService",
            make_rbac_service(allow=True),
        )

        dependency = deps_module.require_permission("alerts.view")

        result = dependency(membership=fake_membership, db=fake_db)

        assert result is fake_membership

    def test_permission_matched_from_role_permission_list(
        self, deps_module, fake_membership, fake_db, monkeypatch
    ):
        # Drive the real allow/deny logic off a concrete permission list
        # instead of forcing the boolean.
        monkeypatch.setattr(
            deps_module,
            "RBACService",
            make_rbac_service(permissions=["alerts.view", "incidents.view"]),
        )

        allowed = deps_module.require_permission("alerts.view")
        denied = deps_module.require_permission("tenants.delete")

        assert allowed(membership=fake_membership, db=fake_db) is fake_membership

        with pytest.raises(HTTPException) as exc_info:
            denied(membership=fake_membership, db=fake_db)
        assert exc_info.value.status_code == HTTP_403_FORBIDDEN

    def test_super_permission_grants_any_key(
        self, deps_module, fake_membership, fake_db, monkeypatch
    ):
        # A holder of ``platform.all`` passes every permission check.
        monkeypatch.setattr(
            deps_module,
            "RBACService",
            make_rbac_service(permissions=["platform.all"]),
        )

        dependency = deps_module.require_permission("some.arbitrary.permission")

        assert dependency(membership=fake_membership, db=fake_db) is fake_membership


# ======================================================================
# 2b. PERMISSION DENIAL  (require_roles -> legacy membership.role)
# ======================================================================

class TestRequireRoles:
    """
    The legacy ``require_roles`` guard checks the membership's enum role
    against an allow-list. It must unwrap the enum via ``.value`` and reject
    anything not on the list with 403.
    """

    def test_role_not_in_allowlist_is_denied(
        self, deps_module, fake_db
    ):
        membership = FakeMembership(role=MembershipRole.VIEWER)
        dependency = deps_module.require_roles([MembershipRole.OWNER.value])

        with pytest.raises(HTTPException) as exc_info:
            dependency(membership=membership)

        assert exc_info.value.status_code == HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "forbidden"

    def test_role_in_allowlist_is_allowed(
        self, deps_module, fake_db
    ):
        membership = FakeMembership(role=MembershipRole.OWNER)
        dependency = deps_module.require_roles(
            [MembershipRole.OWNER.value, MembershipRole.ADMIN.value]
        )

        result = dependency(membership=membership)

        assert result is membership


# ======================================================================
# 3. IDENTITY  (get_current_user — unauthenticated rejection)
# ======================================================================

class TestIdentityBoundary:
    """
    ``get_current_user`` must reject a request with no session cookie before
    it ever touches token verification or the database.
    """

    def test_no_session_cookie_is_rejected(self, deps_module, fake_db):
        request = FakeRequest({})  # no session cookie

        with pytest.raises(HTTPException) as exc_info:
            deps_module.get_current_user(request=request, db=fake_db)

        assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "not_authenticated"