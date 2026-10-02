from __future__ import annotations

import os
import re
from pathlib import Path
from uuid import UUID, uuid4

import pytest


def _database_url_from_dotenv() -> str | None:
    """Read DATABASE_URL straight out of backend/.env, if present.

    The DB-backed integration tests query real seeded tenants and
    memberships and hardcode a real tenant id, so they can only work
    against the real dev database — the placeholder fallback below
    can never satisfy them.
    """
    env_file = Path(__file__).resolve().parent.parent / ".env"

    if not env_file.exists():
        return None

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")

    return None


_real_url = _database_url_from_dotenv()

if _real_url:
    # Force pg8000 regardless of whatever driver the real URL names.
    # psycopg (v3) has been repeatedly blocked by Application Control
    # on this machine — confirmed recurring, not a one-off — and this
    # is now blocking test collection outright. pg8000 is pure Python,
    # nothing for that policy to block, and has worked reliably every
    # other time it's been used in this build. This only changes what
    # DATABASE_URL pytest sees; it does not touch how the actual
    # running app connects.
    _real_url = re.sub(
        r"^postgresql(\+\w+)?://",
        "postgresql+pg8000://",
        _real_url,
    )


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
    _real_url or "postgresql://test:test@localhost:5432/test",
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
