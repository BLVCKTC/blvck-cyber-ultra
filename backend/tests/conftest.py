"""
Shared fixtures and fakes for the security-boundary test suite.

These tests target the authorization seams in ``app.api.deps`` directly:

    get_current_user      -> identity        (Keycloak session cookie)
    get_active_membership -> tenant isolation (MembershipRepo)
    require_permission    -> RBAC            (RBACService)
    require_roles         -> legacy RBAC     (membership.role)

They deliberately avoid a live Keycloak server or Postgres connection. The
dependency callables are invoked directly with fake users / memberships, and
the data-access collaborators (``MembershipRepo``, ``RBACService``) are
monkeypatched onto the ``app.api.deps`` module so we can assert the boundary
logic in isolation.

IMPORTANT: ``app.core.config`` builds a pydantic ``Settings()`` instance at
import time, and ``app.core.db`` creates a SQLAlchemy engine from
``DATABASE_URL`` at import time. Both must have values present *before* any
``app.*`` module is imported, so we seed dummy env vars at the very top of this
conftest (before the app imports below).
"""

from __future__ import annotations

import os

# ----------------------------------------------------------------------
# Environment bootstrap — MUST run before importing any app.* module.
# The engine is created lazily and never actually connects in these tests
# (get_db is never exercised against a real session), so a dummy DSN using
# the installed psycopg (v3) driver is sufficient for import to succeed.
# ----------------------------------------------------------------------
os.environ.setdefault("KEYCLOAK_URL", "http://localhost:8080")
os.environ.setdefault("KEYCLOAK_REALM", "test-realm")
os.environ.setdefault("KEYCLOAK_CLIENT_ID", "test-client")
os.environ.setdefault("KEYCLOAK_CLIENT_SECRET", "test-secret")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://test:test@localhost:5432/test",
)

from dataclasses import dataclass, field  # noqa: E402

import pytest  # noqa: E402

from app.api import deps  # noqa: E402
from app.db.models.enums import MembershipRole  # noqa: E402


# ======================================================================
# FAKES
# ======================================================================

@dataclass
class FakeUser:
    """Stand-in for a persisted ``User`` row."""

    id: int = 1
    keycloak_sub: str = "keycloak-sub-1"


@dataclass
class FakeMembership:
    """
    Stand-in for a persisted ``Membership`` row.

    ``role`` is a real ``MembershipRole`` enum so that ``require_roles``
    exercises its ``.value`` unwrapping exactly as it does in production.
    """

    user_id: int = 1
    tenant_id: str = "TENANT-A"
    role: MembershipRole = MembershipRole.SOC_ANALYST
    tenant_role_id: int | None = 1


class FakeRequest:
    """Minimal Starlette-Request stand-in exposing only ``.cookies``."""

    def __init__(self, cookies: dict[str, str] | None = None):
        self.cookies = dict(cookies or {})


def make_membership_repo(result):
    """Build a fake MembershipRepo class whose lookups return ``result``."""

    class _FakeMembershipRepo:
        def __init__(self, db):
            self.db = db

        def get_membership(self, user_id, tenant_id):
            return result

    return _FakeMembershipRepo


def make_rbac_service(*, permissions: list[str] | None = None, allow: bool | None = None):
    """
    Build a fake RBACService class.

    - ``allow`` (when set) forces ``has_permission`` to that value.
    - ``permissions`` (when set) drives the real membership/super-permission
      logic by returning that permission list from ``get_permissions``.
    """

    perms = list(permissions or [])

    class _FakeRBACService:
        SUPER_PERMISSION = "platform.all"

        def __init__(self, db):
            self.db = db

        def get_permissions(self, user_id, tenant_id):
            return perms

        def has_permission(self, user_id, tenant_id, permission_key):
            if allow is not None:
                return allow
            granted = set(perms)
            if self.SUPER_PERMISSION in granted:
                return True
            return permission_key in granted

    return _FakeRBACService


# ======================================================================
# FIXTURES
# ======================================================================

@pytest.fixture
def deps_module():
    """The imported ``app.api.deps`` module under test."""
    return deps


@pytest.fixture
def fake_user():
    return FakeUser()


@pytest.fixture
def fake_membership():
    return FakeMembership()


@pytest.fixture
def fake_db():
    """A sentinel db handle — never touched because collaborators are faked."""
    return object()
