"""
Security-boundary test suite (Recommendation #6).

These tests exercise the three authorization seams that live in
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

3. AI-cannot-execute -> documented skip
     The product has no AI/agent execution layer yet, so there is no seam to
     assert against. The test is scaffolded and skipped so the intent is
     recorded and the suite fails loudly the day someone wires an AI actor in
     without a guard. See the test body for the contract it must satisfy.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)

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
    reads the ``tenant_id`` cookie and looks up a membership for
    ``(user.id, tenant_id)``. If none exists the request is rejected 403 —
    this is what stops a user in TENANT-A from reaching TENANT-B's data.
    """

    def test_cross_tenant_access_is_denied(
        self, deps_module, fake_user, fake_db, monkeypatch
    ):
        # The attacker presents a valid session but points the tenant cookie
        # at a tenant they do NOT belong to. The repo therefore finds nothing.
        monkeypatch.setattr(
            deps_module,
            "MembershipRepo",
            make_membership_repo(None),
        )

        request = FakeRequest({deps_module.ACTIVE_TENANT_COOKIE_NAME: "TENANT-B"})

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
        # The user IS a member of the tenant they select -> membership returned.
        membership = FakeMembership(user_id=fake_user.id, tenant_id="TENANT-A")

        monkeypatch.setattr(
            deps_module,
            "MembershipRepo",
            make_membership_repo(membership),
        )

        request = FakeRequest({deps_module.ACTIVE_TENANT_COOKIE_NAME: "TENANT-A"})

        result = deps_module.get_active_membership(
            request=request,
            db=fake_db,
            user=fake_user,
        )

        assert result is membership
        assert result.tenant_id == "TENANT-A"

    def test_missing_tenant_cookie_is_denied(
        self, deps_module, fake_user, fake_db, monkeypatch
    ):
        # No tenant selected at all -> 401 before any membership lookup runs.
        # Guard the repo so an accidental lookup would blow up the test.
        monkeypatch.setattr(
            deps_module,
            "MembershipRepo",
            make_membership_repo(FakeMembership()),
        )

        request = FakeRequest({})  # no tenant cookie

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


# ======================================================================
# 4. AI-CANNOT-EXECUTE  (scaffolded, skipped until an AI layer exists)
# ======================================================================

@pytest.mark.skip(
    reason=(
        "No AI/agent execution layer exists yet, so there is no seam to "
        "assert against. When one is added, an AI actor MUST route through "
        "the same authorization dependencies as a human — it must NOT be "
        "able to invoke privileged/state-changing operations directly. "
        "Un-skip and implement the contract described in the test body."
    )
)
def test_ai_actor_cannot_execute_privileged_operations():
    """
    Contract to enforce once an AI layer lands:

    * An AI-initiated action carries an actor identity (service principal or
      the delegating user) and MUST pass through ``get_active_membership`` +
      ``require_permission`` exactly like a human request.
    * An AI actor with NO membership in the target tenant is rejected 403.
    * An AI actor without the required permission is rejected 403 — there is
      no "AI bypass" path around ``require_permission``.
    * Any tool/function the AI can call that mutates state must be guarded by
      a permission dependency, not merely reachable because the AI is trusted.
    """
    raise AssertionError("AI execution boundary not yet implemented")
