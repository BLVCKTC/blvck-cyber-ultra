from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.backtest import BacktestMatch, BacktestRun
from app.db.repositories.detection_rule_repo import DetectionRuleRepository
from app.services.detection_rules.execution import RuleExecutor


class BacktestNotFoundError(Exception):
    """Raised when the target rule doesn't exist for this tenant."""


class BacktestService:
    """Orchestrates running a detection rule against a historical
    window and persisting what fired.

    Does NOT compute precision/false-positive rate — that needs labeled
    ground truth tied to specific historical events, which doesn't
    connect to backtest candidates anywhere in this codebase yet
    (AlertFeedback is tied to live Alert rows, not backtest matches).
    This only records what the rule would have fired on and why.
    """

    def __init__(self, db: Session):
        self.db = db

    def run_backtest(
        self,
        *,
        tenant_id: UUID,
        rule_id: UUID,
        window_start: datetime,
        window_end: datetime,
        requested_by_id: UUID | None = None,
    ) -> BacktestRun:
        # ASSUMPTION: DetectionRuleRepository lives at this import path
        # and exposes get(*, tenant_id, rule_id) -> DetectionRule | None,
        # based on the fake used in the RuleValidator test file. Not
        # verified against the real repo source.
        repo = DetectionRuleRepository(self.db)
        rule = repo.get(tenant_id=tenant_id, rule_id=rule_id)

        if rule is None:
            raise BacktestNotFoundError(f"Detection rule {rule_id} not found")

        run = BacktestRun(
            id=uuid4(),
            tenant_id=tenant_id,
            detection_rule_id=rule_id,
            window_start=window_start,
            window_end=window_end,
            status="running",
            requested_by_id=requested_by_id,
        )
        self.db.add(run)
        self.db.flush()  # assigns run.id without committing yet

        executor = RuleExecutor(session=self.db, tenant_id=tenant_id)

        try:
            candidates = executor.run(rule, window_start, window_end)
        except Exception as exc:
            run.status = "failed"
            run.error_message = str(exc)
            run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(run)
            return run

        for candidate in candidates:
            self.db.add(
                BacktestMatch(
                    id=uuid4(),
                    backtest_run_id=run.id,
                    window_start=candidate.window_start,
                    window_end=candidate.window_end,
                    group_key=candidate.group_key,
                    metric_value=candidate.metric_value,
                    event_ids=candidate.event_ids,
                )
            )

        run.status = "completed"
        run.total_candidates = len(candidates)
        run.completed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(run)
        return run

    def get_backtest(self, *, tenant_id: UUID, run_id: UUID) -> BacktestRun | None:
        run = self.db.get(BacktestRun, run_id)
        if run is None or run.tenant_id != tenant_id:
            return None
        return run

    def list_matches(self, *, tenant_id: UUID, run_id: UUID) -> list[BacktestMatch]:
        run = self.get_backtest(tenant_id=tenant_id, run_id=run_id)
        if run is None:
            return []
        return (
            self.db.query(BacktestMatch)
            .filter(BacktestMatch.backtest_run_id == run_id)
            .order_by(BacktestMatch.window_start)
            .all()
        )