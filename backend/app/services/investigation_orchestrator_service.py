from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.state import _DEFAULT_PLAN  # state.py has no langgraph import

# Backstop against a node that neither completes nor errors. Planned steps
# plus load_context, planner and reporting, with headroom. Tighter than
# LangGraph's default of 25 so a loop fails fast.
_RECURSION_LIMIT = len(_DEFAULT_PLAN) + 10


class OrchestrationError(Exception):
    def __init__(
        self,
        message: str,
        *,
        failed_step: str | None = None,
        investigation_id: str | None = None,
        run_id: str | None = None,
        completed_steps: list[str] | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.failed_step = failed_step
        self.investigation_id = investigation_id
        self.run_id = run_id
        self.completed_steps = completed_steps or []
        self.code = code


class InvestigationOrchestratorService:
    """Thin wrapper triggering the investigation graph. Deliberately
    explicit-call-only for this skeleton — NOT wired into ingest().

    The langgraph import is deferred to run_for_alert() rather than
    module level. Importing this service (or anything that imports the
    route file that imports this service — which includes app.main,
    and therefore every test that boots the app) must not require
    langgraph's import chain to succeed. On this machine specifically,
    langgraph pulls in ormsgpack for checkpoint serialization, which
    has hit the same Application Control DLL block psycopg did — a
    real, still-open problem, but one that should only affect actually
    calling the orchestrator, not booting the app or running unrelated
    tests.
    """

    def __init__(self, db: Session):
        self.db = db

    def run_for_alert(self, *, tenant_id: UUID, alert_id: UUID) -> dict:
        # Deferred: see class docstring.
        from langgraph.errors import GraphRecursionError

        from app.agents.orchestrator import build_investigation_graph

        graph = build_investigation_graph(self.db)

        try:
            result = graph.invoke(
                {
                    "tenant_id": str(tenant_id),
                    "alert_id": str(alert_id),
                },
                config={"recursion_limit": _RECURSION_LIMIT},
            )
        except GraphRecursionError as exc:
            self.db.rollback()
            raise OrchestrationError(
                "Orchestration exceeded its step limit; a node likely "
                "failed to mark itself complete or set an error."
            ) from exc
        except Exception:
            self.db.rollback()
            raise

        if result.get("error"):
            raise OrchestrationError(
                result["error"],
                failed_step=result.get("failed_step"),
                investigation_id=result.get("investigation_id"),
                run_id=result.get("run_id"),
                completed_steps=list(result.get("completed_steps", [])),
                code=result.get("error_code"),
            )

        return result