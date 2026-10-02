"""
Agent authority boundary (Part 1 of the handoff: no agent may move from an
untrusted event to an irreversible action without a human).

The orchestrator has no principal of its own: it runs inside the requesting
user's session. So the boundary is enforced in three places:

1. The orchestrate route sits behind the same auth chain as any human
   request, and requires BOTH ai.assistant.use (trigger the run) and
   forensics.manage (the run writes investigations and evidence, so the
   caller must hold that authority directly).
2. Agent code can only import an explicit allowlist of modules. Anything
   state-changing (response actions, rule governance, audit) is absent, so
   adding one fails here and forces a conscious decision.
3. A real run changes only investigations and evidence for the tenant.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

from sqlalchemy import text

from app.db.base import Base
from tests.test_investigation_agents import TENANT_ID, seeded_alert

AGENTS_DIR = Path(__file__).resolve().parents[1] / "app" / "agents"

# Every app.* module agent code may import. Extending this list is a
# deliberate act: ask whether the new module lets an agent act on its own.
ALLOWED_APP_IMPORTS = (
    "app.agents",
    "app.db.models.alert",
    "app.db.models.security_event",
    "app.db.models.detection_rule",       # read-only context
    "app.db.models.mitre",                # read-only context
    "app.db.models.intelligence",         # Indicator, read-only
    "app.db.models.asset",                # tolerated if Indicator lives here
    "app.db.models.investigation",
    "app.schemas.investigation",
    "app.services.investigation_service",
)

FORBIDDEN_NAMES = {"importlib", "__import__", "eval", "exec"}

ALLOWED_WRITE_TABLES = {"investigations", "evidence"}

# The route must be guarded by every one of these.
ORCHESTRATE_PERMISSIONS = {"ai.assistant.use", "forensics.manage"}

# The router prefix is /investigations, so the route's own path ends here.
ORCHESTRATE_PATH_SUFFIX = "/investigations/orchestrate/{alert_id}"


# ----------------------------------------------------------------------
# 1. Static: agent code cannot reach action paths
# ----------------------------------------------------------------------

def _agent_files() -> list[Path]:
    return sorted(
        p for p in AGENTS_DIR.rglob("*.py") if "__pycache__" not in p.parts
    )


def _app_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [a.name for a in node.names if a.name.startswith("app")]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                found.append(f"<relative import in {path.name}>")
                continue
            module = node.module or ""
            if module.startswith("app"):
                # "from app.db.models import X" -> check app.db.models.X
                found += [f"{module}.{a.name}" for a in node.names]

    return found


def test_agent_code_imports_only_allowlisted_app_modules():
    assert _agent_files(), f"no agent files found under {AGENTS_DIR}"

    violations = []
    for path in _agent_files():
        for name in _app_imports(path):
            if not any(name.startswith(prefix) for prefix in ALLOWED_APP_IMPORTS):
                violations.append(f"{path.relative_to(AGENTS_DIR)}: {name}")

    assert not violations, (
        "Agent code imports modules outside the authority allowlist. If a "
        "module is read-only, add it to ALLOWED_APP_IMPORTS; if it can "
        "change state or act, route it through a human approval gate "
        "instead:\n" + "\n".join(violations)
    )


def test_agent_code_has_no_dynamic_import_escape_hatches():
    violations = []
    for path in _agent_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Name):
                names = [node.id]
            elif isinstance(node, ast.Attribute):
                names = [node.attr]
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name.split(".")[0] for a in node.names]
            for n in names:
                if n in FORBIDDEN_NAMES:
                    violations.append(f"{path.relative_to(AGENTS_DIR)}: {n}")

    assert not violations, "\n".join(sorted(set(violations)))


# ----------------------------------------------------------------------
# 2. Route wiring: same auth chain as a human request
# ----------------------------------------------------------------------

def _walk(dependant):
    for sub in dependant.dependencies:
        yield sub.call
        yield from _walk(sub)


def _iter_routes(routes):
    """
    Yield every concrete route.

    This FastAPI version wraps included routers in _IncludedRouter objects
    (no .path); the real router is on .original_router. Mounted sub-apps
    expose their routes through .app.
    """
    for r in routes:
        original = getattr(r, "original_router", None)
        if original is not None:
            yield from _iter_routes(original.routes)
            continue

        yield r

        sub = getattr(r, "app", None)
        if sub is not None and hasattr(sub, "routes"):
            yield from _iter_routes(sub.routes)


def _orchestrate_route():
    from app.main import app

    routes = [
        r
        for r in _iter_routes(app.routes)
        if getattr(r, "path", "").endswith(ORCHESTRATE_PATH_SUFFIX)
        and "POST" in (getattr(r, "methods", None) or ())
    ]
    assert len(routes) == 1, (
        f"expected exactly one POST route ending in "
        f"{ORCHESTRATE_PATH_SUFFIX}, found {len(routes)}"
    )
    return routes[0]


def test_orchestrate_route_uses_the_human_auth_chain(deps_module):
    calls = list(_walk(_orchestrate_route().dependant))

    assert deps_module.get_current_user in calls, "no session auth"
    assert deps_module.get_active_membership in calls, "no tenant membership"

    permission_guards = [
        c for c in calls if "require_permission" in getattr(c, "__qualname__", "")
    ]
    assert permission_guards, "route has no require_permission guard"

    # Each guard must carry its key (a closure variable), not merely exist.
    # This is the permission-string bug class from the handoff.
    keys = set()
    for guard in permission_guards:
        for value in inspect.getclosurevars(guard).nonlocals.values():
            if isinstance(value, str):
                keys.add(value)

    missing = ORCHESTRATE_PERMISSIONS - keys
    assert not missing, (
        f"orchestrate route is missing required permission guard(s) "
        f"{sorted(missing)}; guards carry: {sorted(keys)}"
    )


# ----------------------------------------------------------------------
# 3. Behavioral: a real run only writes investigations + evidence
# ----------------------------------------------------------------------

def _tenant_tables() -> list[str]:
    return sorted(
        t.name for t in Base.metadata.sorted_tables if "tenant_id" in t.c
    )


def _fingerprints(db) -> dict[str, tuple[int, str]]:
    """Per-table (row count, content hash) for the test tenant."""
    db.rollback()  # fresh transaction so RLS context is re-applied
    out = {}
    for name in _tenant_tables():
        row = db.execute(
            text(
                f'SELECT count(*), '
                f"md5(coalesce(string_agg(t::text, '|' ORDER BY t::text), '')) "
                f'FROM "{name}" t WHERE t.tenant_id = :tid'
            ),
            {"tid": TENANT_ID},
        ).one()
        out[name] = (row[0], row[1])
    db.rollback()
    return out


def test_orchestrator_run_changes_only_investigations_and_evidence():
    from app.services.investigation_orchestrator_service import (
        InvestigationOrchestratorService,
    )

    with seeded_alert(rule_mitre=False, indicator_value="203.0.113.7") as (
        db,
        tid,
        ids,
    ):
        before = _fingerprints(db)

        InvestigationOrchestratorService(db).run_for_alert(
            tenant_id=tid, alert_id=ids["alert"]
        )

        after = _fingerprints(db)

    changed = {name for name in before if before[name] != after[name]}

    # Sanity: the check can see changes at all.
    assert {"investigations", "evidence"} <= changed, (
        f"expected the run to write investigations and evidence; saw {changed}"
    )

    unexpected = changed - ALLOWED_WRITE_TABLES
    assert not unexpected, (
        f"orchestrator run modified tables outside its authority: "
        f"{sorted(unexpected)}"
    )