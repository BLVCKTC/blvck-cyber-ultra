from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.backtest import BacktestRun
from app.db.models.canary import CanaryMatch
from app.db.models.detection_rule import DetectionRuleStatus
from app.db.repositories.detection_rule_repo import DetectionRuleRepository

MIN_CANARY_DAYS = 7
MAX_DEVIATION_PERCENT = 50.0


@dataclass(slots=True)
class CanaryPromotionStatus:
    rule_id: UUID
    eligible: bool
    reasons: list[str]
    days_in_canary: float | None
    canary_match_count: int
    canary_rate_per_day: float | None
    backtest_match_count: int | None
    backtest_rate_per_day: float | None
    deviation_percent: float | None


class CanaryPromotionService:
    """Advisory only. Reports whether a CANARY rule looks eligible for
    APPROVED, by comparing its live match rate since entering canary
    against its own most recent completed backtest. Does NOT transition
    the rule — a human still calls DetectionRuleService.transition() to
    actually promote it, with all of that method's existing governance
    checks (validation, separation of duties) applying in full and
    completely independent of this gate.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_status(
        self,
        *,
        tenant_id: UUID,
        rule_id: UUID,
    ) -> CanaryPromotionStatus:
        rule = DetectionRuleRepository(self.db).get(
            tenant_id=tenant_id, rule_id=rule_id
        )

        if rule is None:
            raise ValueError(f"Detection rule {rule_id} not found")

        reasons: list[str] = []

        if DetectionRuleStatus(rule.status) != DetectionRuleStatus.CANARY:
            reasons.append(f"Rule is '{rule.status}', not 'canary'.")
            return self._empty(rule_id, reasons)

        canary_started_at = rule.canary_started_at

        if canary_started_at is None:
            reasons.append(
                "Rule has no canary_started_at recorded — it entered "
                "CANARY before this field existed, or via a code path "
                "that doesn't set it."
            )
            return self._empty(rule_id, reasons)

        now = datetime.now(timezone.utc)
        days_in_canary = (now - canary_started_at).total_seconds() / 86400.0

        if days_in_canary < MIN_CANARY_DAYS:
            reasons.append(
                f"Only {days_in_canary:.1f} days in canary; "
                f"minimum is {MIN_CANARY_DAYS}."
            )

        canary_match_count = (
            self.db.scalar(
                select(func.count(CanaryMatch.id)).where(
                    CanaryMatch.detection_rule_id == rule_id,
                    CanaryMatch.matched_at >= canary_started_at,
                )
            )
            or 0
        )
        canary_rate_per_day = (
            canary_match_count / days_in_canary if days_in_canary > 0 else 0.0
        )

        latest_backtest = self.db.scalar(
            select(BacktestRun)
            .where(
                BacktestRun.detection_rule_id == rule_id,
                BacktestRun.status == "completed",
            )
            .order_by(BacktestRun.completed_at.desc())
            .limit(1)
        )

        backtest_match_count: int | None = None
        backtest_rate_per_day: float | None = None
        deviation_percent: float | None = None

        if latest_backtest is None:
            reasons.append(
                "No completed backtest run found for this rule — cannot "
                "compute a divergence baseline."
            )
        else:
            backtest_match_count = latest_backtest.total_candidates
            backtest_window_days = (
                latest_backtest.window_end - latest_backtest.window_start
            ).total_seconds() / 86400.0
            backtest_rate_per_day = (
                backtest_match_count / backtest_window_days
                if backtest_window_days > 0
                else 0.0
            )

            # Floor avoids a divide-by-zero when the backtest found
            # nothing; a rule that never matched historically but is
            # matching live is itself a real, worth-surfacing signal,
            # not a bug in this calculation.
            baseline = max(backtest_rate_per_day, 0.01)
            deviation_percent = (
                abs(canary_rate_per_day - backtest_rate_per_day)
                / baseline
                * 100.0
            )

            if deviation_percent > MAX_DEVIATION_PERCENT:
                reasons.append(
                    f"Live match rate diverges {deviation_percent:.1f}% "
                    f"from backtest baseline; threshold is "
                    f"{MAX_DEVIATION_PERCENT}%."
                )

        return CanaryPromotionStatus(
            rule_id=rule_id,
            eligible=not reasons,
            reasons=reasons,
            days_in_canary=days_in_canary,
            canary_match_count=canary_match_count,
            canary_rate_per_day=canary_rate_per_day,
            backtest_match_count=backtest_match_count,
            backtest_rate_per_day=backtest_rate_per_day,
            deviation_percent=deviation_percent,
        )

    @staticmethod
    def _empty(rule_id: UUID, reasons: list[str]) -> CanaryPromotionStatus:
        return CanaryPromotionStatus(
            rule_id=rule_id,
            eligible=False,
            reasons=reasons,
            days_in_canary=None,
            canary_match_count=0,
            canary_rate_per_day=None,
            backtest_match_count=None,
            backtest_rate_per_day=None,
            deviation_percent=None,
        )