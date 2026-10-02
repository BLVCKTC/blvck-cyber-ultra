from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.alert import Alert
from app.db.models.intelligence import Indicator
from app.db.models.security_event import SecurityEvent

CANDIDATE_CAP = 200
MATCH_CAP = 50
MIN_LEN = 3
MAX_LEN = 512  # Indicator.value is String(512)
MAX_DEPTH = 5
LIST_CAP = 50
NODE_BUDGET = 2000
PATHS_PER_VALUE = 5


class _Candidates:
    """Normalized lookup value -> where in the event it was seen."""

    def __init__(self) -> None:
        self.by_key: dict[str, list[str]] = {}
        self.truncated = False

    def add(self, path: str, value: Any) -> None:
        if value is None:
            return
        text = str(value).strip()
        if not (MIN_LEN <= len(text) <= MAX_LEN):
            return
        key = text.lower()
        if key not in self.by_key:
            if len(self.by_key) >= CANDIDATE_CAP:
                self.truncated = True
                return
            self.by_key[key] = []
        paths = self.by_key[key]
        if len(paths) < PATHS_PER_VALUE and path not in paths:
            paths.append(path)


def _walk_strings(obj: Any, prefix: str, cands: _Candidates) -> None:
    """Bounded iterative walk adding every string leaf as a candidate."""
    budget = NODE_BUDGET
    stack: list[tuple[Any, str, int]] = [(obj, prefix, 0)]
    while stack and budget > 0:
        current, path, depth = stack.pop()
        budget -= 1
        if isinstance(current, str):
            cands.add(path, current)
        elif isinstance(current, Mapping) and depth < MAX_DEPTH:
            # Reverse-sorted push so pops come out in ascending key order.
            for key in sorted(current, key=str, reverse=True):
                stack.append((current[key], f"{path}.{key}", depth + 1))
        elif isinstance(current, (list, tuple)) and depth < MAX_DEPTH:
            for i in range(min(len(current), LIST_CAP) - 1, -1, -1):
                stack.append((current[i], f"{path}[{i}]", depth + 1))
    if budget <= 0 and stack:
        cands.truncated = True


def collect_threat_intel_context(
    db: Session,
    *,
    tenant_id: UUID,
    alert_id: UUID,
) -> dict[str, Any] | None:
    """
    Read-only lookup of the alert's event values against the tenant's local
    Indicator table. Local store only: no external feeds are consulted.

    Returns {"note": str, "data": JSON-safe dict}, or None when the alert is
    missing or belongs to another tenant. Never writes or commits.
    """
    alert = db.get(Alert, alert_id)
    if alert is None or alert.tenant_id != tenant_id:
        return None

    gaps: list[str] = []

    event: SecurityEvent | None = None
    if alert.security_event_id is None:
        gaps.append("no_event_linked")
    else:
        event = db.get(SecurityEvent, alert.security_event_id)
        if event is not None and event.tenant_id != tenant_id:
            event = None
        if event is None:
            gaps.append("event_missing_or_deleted")

    cands = _Candidates()
    if event is not None:
        # Typed columns first, so they are never crowded out by the cap.
        cands.add("source_ip", event.source_ip)
        cands.add("destination_ip", event.destination_ip)
        cands.add("hostname", event.hostname)
        cands.add("user_identifier", event.user_identifier)
        _walk_strings(event.normalized_data or {}, "normalized_data", cands)
        _walk_strings(event.raw_event or {}, "raw_event", cands)

    if event is not None and not cands.by_key:
        gaps.append("no_candidate_values")
    if cands.truncated:
        gaps.append("candidate_values_truncated")

    rows: list[Indicator] = []
    if cands.by_key:
        # lower() cannot use the (tenant_id, type, value) unique index, so
        # this scans the tenant's indicators. Fine at small scale; see the
        # note on a (tenant_id, lower(value)) index if the table grows.
        rows = list(
            db.execute(
                select(Indicator).where(
                    Indicator.tenant_id == tenant_id,
                    func.lower(Indicator.value).in_(list(cands.by_key)),
                )
            ).scalars()
        )

    rows.sort(key=lambda r: (-(r.confidence if r.confidence is not None else -1), r.value))

    matches = [
        {
            "indicator_type": r.indicator_type,
            "value": r.value,
            "verdict": r.verdict,
            "confidence": r.confidence,
            "source": r.source,
            "matched_on": cands.by_key.get(r.value.strip().lower(), []),
        }
        for r in rows[:MATCH_CAP]
    ]

    data: dict[str, Any] = {
        "scope": "local_indicator_store_only",
        "candidates_checked": len(cands.by_key),
        "matches": matches,
        "matches_total": len(rows),
        "matches_truncated": len(rows) > MATCH_CAP,
        "gaps": gaps,
    }

    if rows:
        verdicts = sorted({r.verdict or "unknown" for r in rows})
        note = (
            f"{len(rows)} local indicator match(es) among "
            f"{len(cands.by_key)} value(s) checked (verdicts: "
            f"{', '.join(verdicts)})"
        )
    else:
        note = (
            f"no matches in local indicator store ({len(cands.by_key)} "
            f"value(s) checked); external feeds not consulted, so this is "
            f"not evidence the values are benign"
        )
    if gaps:
        note += f"; gaps: {', '.join(gaps)}"

    return {"note": note, "data": data}