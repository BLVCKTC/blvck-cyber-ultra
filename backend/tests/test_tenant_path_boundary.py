"""
Tenant resolution for tenant-scoped routes (get_active_membership).

The tenant in the URL path must win over the active-tenant cookie, and
membership must be checked against the path tenant. A cookie for a tenant
the user belongs to must never authorize a request for a different tenant.
"""

from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from tests.conftest import FakeMembership


def _repo_for(member_of: set):
    """MembershipRepo stand-in: the user belongs only to `member_of`."""
    calls: list = []

    class Repo:
        def __init__(self, db):
            pass

        def get_membership(self, user_id, tenant_id):
            calls.append(tenant_id)
            if tenant_id not in member_of:
                return None
            return FakeMembership(user_id=user_id, tenant_id=tenant_id)

    return Repo, calls


def _request(deps_module, *, path_tenant=None, cookie_tenant=None):
    path_params = {"tenant_id": str(path_tenant)} if path_tenant else {}
    cookies = (
        {deps_module.ACTIVE_TENANT_COOKIE_NAME: str(cookie_tenant)}
        if cookie_tenant
        else {}
    )
    return SimpleNamespace(path_params=path_params, cookies=cookies)


def test_path_tenant_wins_over_cookie_tenant(
    deps_module, fake_user, fake_db, monkeypatch
):
    path_tenant, cookie_tenant = uuid4(), uuid4()
    repo, calls = _repo_for({path_tenant, cookie_tenant})
    monkeypatch.setattr(deps_module, "MembershipRepo", repo)

    result = deps_module.get_active_membership(
        request=_request(
            deps_module, path_tenant=path_tenant, cookie_tenant=cookie_tenant
        ),
        db=fake_db,
        user=fake_user,
    )

    assert result.tenant_id == path_tenant
    assert calls == [path_tenant], "cookie tenant must not be consulted"


def test_cookie_membership_does_not_authorize_a_different_path_tenant(
    deps_module, fake_user, fake_db, monkeypatch
):
    path_tenant, cookie_tenant = uuid4(), uuid4()
    # The user belongs to the cookie tenant only.
    repo, calls = _repo_for({cookie_tenant})
    monkeypatch.setattr(deps_module, "MembershipRepo", repo)

    with pytest.raises(HTTPException) as exc_info:
        deps_module.get_active_membership(
            request=_request(
                deps_module,
                path_tenant=path_tenant,
                cookie_tenant=cookie_tenant,
            ),
            db=fake_db,
            user=fake_user,
        )

    assert exc_info.value.status_code == HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "not_a_member"
    assert calls == [path_tenant]


def test_malformed_path_tenant_is_rejected(
    deps_module, fake_user, fake_db, monkeypatch
):
    repo, calls = _repo_for(set())
    monkeypatch.setattr(deps_module, "MembershipRepo", repo)

    request = SimpleNamespace(
        path_params={"tenant_id": "not-a-uuid"}, cookies={}
    )

    with pytest.raises(HTTPException) as exc_info:
        deps_module.get_active_membership(
            request=request, db=fake_db, user=fake_user
        )

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "invalid_tenant_id"
    assert calls == [], "no membership lookup for an invalid tenant id"


def test_cookie_is_used_only_when_the_route_has_no_tenant_in_its_path(
    deps_module, fake_user, fake_db, monkeypatch
):
    cookie_tenant = uuid4()
    repo, calls = _repo_for({cookie_tenant})
    monkeypatch.setattr(deps_module, "MembershipRepo", repo)

    result = deps_module.get_active_membership(
        request=_request(deps_module, cookie_tenant=cookie_tenant),
        db=fake_db,
        user=fake_user,
    )

    assert result.tenant_id == cookie_tenant
    assert calls == [cookie_tenant]