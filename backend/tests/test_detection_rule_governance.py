"""
Tests for detection-rule lifecycle governance: reviewer/approval
separation-of-duties enforcement in ``DetectionRuleService.transition``.

Follows the same fake/monkeypatch convention as
``test_security_boundaries.py`` — no live DB. ``DetectionRuleRepository``
is replaced with an in-memory fake so we can assert the authorization
logic in ``DetectionRuleService`` in isolation from persistence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

import app.services.detection_rule_service as detection_rule_service_module
from app.db.models.detection_rule import DetectionRule, DetectionRuleStatus
from app.services.detection_rule_service import (
    DetectionRuleService,
    SeparationOfDutiesError,
)


# ======================================================================
# FAKES
# ======================================================================

class FakeDetectionRuleRepository:
    """In-memory stand-in for DetectionRuleRepository.

    Mirrors only the surface DetectionRuleService.transition() uses:
    get() and update(). update() applies the dict onto the in-memory
    rule and returns it, same shape as the real repo's ORM update.
    """

    def __init__(self, db):
        self._db = db  # unused; matches real repo's __init__(db) signature

    def bind(self, rule: DetectionRule):
        self._rule = rule
        return self

    def get(self, *, tenant_id, rule_id):
        if self._rule.tenant_id != tenant_id or self._rule.id != rule_id:
            return None
        return self._rule

    def update(self, *, tenant_id, rule_id, data):
        for key, value in data.items():
            setattr(self._rule, key, value)
        return self._rule


@pytest.fixture
def fake_repo(monkeypatch):
    """Patch DetectionRuleRepository at the point DetectionRuleService
    imports it, and return the (unbound) fake class instance-to-be so
    each test can bind its own rule.
    """
    holder: dict[str, FakeDetectionRuleRepository] = {}

    def _factory(db):
        repo = FakeDetectionRuleRepository(db)
        holder["repo"] = repo
        return repo

    monkeypatch.setattr(
        detection_rule_service_module,
        "DetectionRuleRepository",
        _factory,
    )
    return holder


def make_rule(
    *,
    status: DetectionRuleStatus,
    created_by_id,
    reviewed_by_id=None,
) -> DetectionRule:
    """A structurally-valid threshold rule so validation failures in
    these tests can only come from the governance checks, not from
    unrelated structure/MITRE/syntax problems.
    """
    return DetectionRule(
        id=uuid4(),
        tenant_id=TENANT_ID,
        name="Excessive failed logins",
        rule_type="threshold",
        severity="medium",
        status=status.value,
        version=1,
        enabled=True,
        query=None,
        configuration={
            "metric": "event_count",
            "operator": "gt",
            "threshold": 5,
            "window_seconds": 300,
        },
        tags=[],
        mitre_technique_ids=["T1110"],
        mitre_tactic_ids=[],
        author=None,
        source=None,
        created_by_id=created_by_id,
        reviewed_by_id=reviewed_by_id,
        reviewed_at=datetime.now(timezone.utc) if reviewed_by_id else None,
    )


TENANT_ID = uuid4()


def build_service(fake_repo, rule: DetectionRule) -> DetectionRuleService:
    svc = DetectionRuleService(db=object())
    fake_repo["repo"].bind(rule)
    return svc


# ======================================================================
# DRAFT -> TESTING (peer review gate)
# ======================================================================

def test_author_cannot_review_own_rule(fake_repo):
    author_id = uuid4()
    rule = make_rule(status=DetectionRuleStatus.DRAFT, created_by_id=author_id)
    svc = build_service(fake_repo, rule)

    with pytest.raises(SeparationOfDutiesError):
        svc.transition(
            tenant_id=TENANT_ID,
            rule_id=rule.id,
            target_status="testing",
            actor_id=author_id,
        )

    # Rejected before any governance fields were stamped.
    assert rule.status == DetectionRuleStatus.DRAFT.value
    assert rule.reviewed_by_id is None


def test_different_reviewer_can_move_draft_to_testing(fake_repo):
    author_id = uuid4()
    reviewer_id = uuid4()
    rule = make_rule(status=DetectionRuleStatus.DRAFT, created_by_id=author_id)
    svc = build_service(fake_repo, rule)

    result = svc.transition(
        tenant_id=TENANT_ID,
        rule_id=rule.id,
        target_status="testing",
        actor_id=reviewer_id,
        notes="Looks reasonable, testing against last 30d.",
    )

    assert result.status == DetectionRuleStatus.TESTING.value
    assert result.reviewed_by_id == reviewer_id
    assert result.reviewed_at is not None
    assert result.review_notes == "Looks reasonable, testing against last 30d."


def test_rule_with_no_author_on_file_does_not_block_review(fake_repo):
    """created_by_id is nullable (SET NULL on user deletion, and legacy
    pre-migration rows are NULL). Self-review can't be evaluated when
    there's no recorded author, so it must not block review is denied by default,
    only compared when created_by_id is actually set.
    """
    reviewer_id = uuid4()
    rule = make_rule(status=DetectionRuleStatus.DRAFT, created_by_id=None)
    svc = build_service(fake_repo, rule)

    result = svc.transition(
        tenant_id=TENANT_ID,
        rule_id=rule.id,
        target_status="testing",
        actor_id=reviewer_id,
    )

    assert result.status == DetectionRuleStatus.TESTING.value
    assert result.reviewed_by_id == reviewer_id


# ======================================================================
# CANARY -> APPROVED (approval gate)
# ======================================================================

def test_author_cannot_approve_own_rule(fake_repo):
    author_id = uuid4()
    reviewer_id = uuid4()
    rule = make_rule(
        status=DetectionRuleStatus.CANARY,
        created_by_id=author_id,
        reviewed_by_id=reviewer_id,
    )
    svc = build_service(fake_repo, rule)

    with pytest.raises(SeparationOfDutiesError):
        svc.transition(
            tenant_id=TENANT_ID,
            rule_id=rule.id,
            target_status="approved",
            actor_id=author_id,
        )

    assert rule.status == DetectionRuleStatus.CANARY.value
    assert rule.approved_by_id is None


def test_reviewer_can_also_be_approver(fake_repo):
    """Separation of duties requires reviewer/approver != author. It
    does NOT require reviewer != approver — the spec only calls out
    the requester/approver distinction for response actions and the
    peer-review step here; a second independent reviewer for approval
    isn't mandated separately.
    """
    author_id = uuid4()
    reviewer_id = uuid4()
    rule = make_rule(
        status=DetectionRuleStatus.CANARY,
        created_by_id=author_id,
        reviewed_by_id=reviewer_id,
    )
    svc = build_service(fake_repo, rule)

    result = svc.transition(
        tenant_id=TENANT_ID,
        rule_id=rule.id,
        target_status="approved",
        actor_id=reviewer_id,
    )

    assert result.status == DetectionRuleStatus.APPROVED.value
    assert result.approved_by_id == reviewer_id
    assert result.approved_at is not None


def test_cannot_approve_before_peer_review(fake_repo):
    author_id = uuid4()
    someone_else = uuid4()
    rule = make_rule(
        status=DetectionRuleStatus.CANARY,
        created_by_id=author_id,
        reviewed_by_id=None,
    )
    svc = build_service(fake_repo, rule)

    with pytest.raises(ValueError) as exc_info:
        svc.transition(
            tenant_id=TENANT_ID,
            rule_id=rule.id,
            target_status="approved",
            actor_id=someone_else,
        )

    assert not isinstance(exc_info.value, SeparationOfDutiesError)
    assert "peer review" in str(exc_info.value)


# ======================================================================
# Validation still gates transitions, independent of governance
# ======================================================================

def test_invalid_transition_still_rejected_before_governance_checks(fake_repo):
    """testing -> production skips backtested/canary/approved and is
    not in the transition map at all — this should fail on the
    transition-allowed check, not be silently accepted because no
    governance rule happens to apply to it.
    """
    author_id = uuid4()
    someone_else = uuid4()
    rule = make_rule(status=DetectionRuleStatus.TESTING, created_by_id=author_id)
    svc = build_service(fake_repo, rule)

    with pytest.raises(ValueError) as exc_info:
        svc.transition(
            tenant_id=TENANT_ID,
            rule_id=rule.id,
            target_status="production",
            actor_id=someone_else,
        )

    assert "invalid_transition" in str(exc_info.value)