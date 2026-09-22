from __future__ import annotations

import os
from uuid import UUID, uuid4

import pytest


os.environ.setdefault(
    "KEYCLOAK_SERVER_URL",
    "http://localhost:8080",
)
os.environ.setdefault(
    "KEYCLOAK_REALM",
    "blvck-cyber",
)
os.environ.setdefault(
    "KEYCLOAK_CLIENT_ID",
    "blvck-cyber",
)
os.environ.setdefault(
    "KEYCLOAK_CLIENT_SECRET",
    "test-secret",
)
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://test:test@localhost:5432/test",
)


TENANT_A = str(uuid4())
TENANT_B = str(uuid4())


class FakeUser:
    def __init__(
        self,
        *,
        user_id: UUID | None = None,
    ) -> None:
        self.id = user_id or uuid4()


class FakeMembership:
    def __init__(
        self,
        *,
        tenant_id: UUID | str | None = None,
        user_id: UUID | str | None = None,
        role: str = "ADMIN",
        permissions: list[str] | None = None,
    ) -> None:
        self.tenant_id = tenant_id if tenant_id is not None else uuid4()
        self.user_id = user_id
        self.role = role
        self.permissions = permissions or []


class FakeRequest:
    def __init__(
        self,
        cookies: dict[str, str] | None = None,
        path_params: dict[str, str] | None = None,
    ) -> None:
        self.cookies = cookies or {}
        self.path_params = path_params or {}


class FakeDB:
    def __init__(self) -> None:
        self.info: dict[str, str] = {}
        self.executed: list[tuple[object, object | None]] = []

    def execute(
        self,
        statement,
        parameters=None,
    ):
        self.executed.append((statement, parameters))
        return None

def make_membership_repo(result):
    class FakeMembershipRepo:
        def __init__(self, db) -> None:
            self.db = db

        def get_for_user_and_tenant(
            self,
            user_id,
            tenant_id,
        ):
            return result

        def get_membership(
            self,
            user_id,
            tenant_id,
        ):
            return result

    return FakeMembershipRepo


def make_rbac_service(
    *,
    allowed: bool = True,
    allow: bool | None = None,
    permissions: list[str] | None = None,
):
    if allow is not None:
        allowed = allow

    class FakeRBACService:
        def __init__(self, db) -> None:
            self.db = db

        def has_permission(
            self,
            *,
            user_id,
            tenant_id,
            permission_key,
        ):
            if permissions is not None:
                if "platform.all" in permissions:
                    return True

                return permission_key in permissions

            return allowed

    return FakeRBACService


@pytest.fixture
def deps_module():
    from app.api import deps

    return deps


@pytest.fixture
def fake_user():
    return FakeUser()


@pytest.fixture
def fake_membership():
    return FakeMembership(
        tenant_id=TENANT_A,
    )


@pytest.fixture
def fake_db():
    return FakeDB()
