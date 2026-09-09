from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.detection_rule import DetectionRuleStatus
from app.db.repositories.detection_rule_repo import DetectionRuleRepository
from app.schemas.detection_rule import (
    DetectionRuleCreate,
    DetectionRuleUpdate,
)
from app.services.detection_rules.validation import RuleValidator


class SeparationOfDutiesError(ValueError):
    """Raised when the same identity would fill two required distinct roles."""


class RuleLockedError(ValueError):
    """Raised when a direct edit is attempted on an approved/live rule.

    Approved and live rules cannot be modified in place because doing so
    would silently change detection logic after it has been reviewed or
    deployed.

    Use ``propose_revision`` to fork the rule into a new draft instead.
    """

_LOCKED_FOR_DIRECT_EDIT = {
    DetectionRuleStatus.APPROVED,
    DetectionRuleStatus.PRODUCTION,
    DetectionRuleStatus.MONITORED,
    DetectionRuleStatus.TUNED,
}

_SUPERSEDABLE_LIVE_STATUSES = {
    DetectionRuleStatus.PRODUCTION,
    DetectionRuleStatus.MONITORED,
    DetectionRuleStatus.TUNED,
}

_FORKABLE_FIELDS = {
    "name",
    "description",
    "rule_type",
    "severity",
    "query",
    "configuration",
    "tags",
    "mitre_technique_ids",
    "mitre_tactic_ids",
    "author",
    "source",
}


class DetectionRuleService:
    """Application service for detection-rule lifecycle management.

    This service is responsible for:

    - tenant-scoped rule access
    - rule creation
    - direct editing of pre-approval rules
    - immutable approved/live rules
    - revision/fork creation
    - lifecycle transitions
    - separation-of-duties enforcement
    - automatic retirement of superseded live rules
    """

    MAX_LIMIT = 500

    def __init__(self, db: Session):
        self.rules = DetectionRuleRepository(db)
        self.validator = RuleValidator()

    def create(
        self,
        *,
        tenant_id: UUID,
        payload: DetectionRuleCreate,
        actor_id: UUID,
    ):
        """Create a new detection rule.

        New rules are created through the repository after attaching the
        identity of the actor who created the rule.
        """

        data = payload.model_dump(mode="python")

        data["created_by_id"] = actor_id

        return self.rules.create(
            tenant_id=tenant_id,
            data=data,
        )

    def get(
        self,
        *,
        tenant_id: UUID,
        rule_id: UUID,
    ):
        """Retrieve a detection rule within the specified tenant."""

        return self.rules.get(
            tenant_id=tenant_id,
            rule_id=rule_id,
        )

    def list(
        self,
        *,
        tenant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        **filters,
    ):
        """Return a paginated tenant-scoped list of detection rules."""

        if not 1 <= limit <= self.MAX_LIMIT:
            raise ValueError(
                f"limit must be between 1 and {self.MAX_LIMIT}"
            )

        if offset < 0:
            raise ValueError(
                "offset must be greater than or equal to 0"
            )

        items = self.rules.list(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            **filters,
        )

        total = self.rules.count(
            tenant_id=tenant_id,
            **filters,
        )

        return items, total

    def update(
        self,
        *,
        tenant_id: UUID,
        rule_id: UUID,
        payload: DetectionRuleUpdate,
    ):
        """Edit a rule in place.

        Direct edits are allowed only before formal approval/live operation.

        Locked states:
            APPROVED
            PRODUCTION
            MONITORED
            TUNED

        If the rule is locked, ``RuleLockedError`` is raised and the caller
        should use ``propose_revision`` instead.
        """

        rule = self.get(
            tenant_id=tenant_id,
            rule_id=rule_id,
        )

        if rule is None:
            return None

        current_status = DetectionRuleStatus(rule.status)

        if current_status in _LOCKED_FOR_DIRECT_EDIT:
            raise RuleLockedError(
                f"Rule is '{rule.status}' and cannot be edited directly; "
                "propose a revision instead"
            )

        data = payload.model_dump(
            mode="python",
            exclude_unset=True,
        )

        if not data:
            raise ValueError(
                "update payload must contain at least one field"
            )

        return self.rules.update(
            tenant_id=tenant_id,
            rule_id=rule_id,
            data=data,
        )

    def delete(
        self,
        *,
        tenant_id: UUID,
        rule_id: UUID,
    ):
        """Delete a detection rule."""

        return self.rules.delete(
            tenant_id=tenant_id,
            rule_id=rule_id,
        )

    def propose_revision(
        self,
        *,
        tenant_id: UUID,
        rule_id: UUID,
        payload: DetectionRuleUpdate,
        actor_id: UUID,
    ):
        """Fork a rule into a new DRAFT revision.

        The source rule is never modified.

        This is particularly important for APPROVED and live rules because
        their current content must remain auditable and reproducible while
        the proposed changes go through the detection lifecycle again.

        Example:

            v1 PRODUCTION
                |
                +----> v2 DRAFT
                         |
                         +--> TESTING
                         +--> BACKTESTED
                         +--> CANARY
                         +--> APPROVED
                         +--> PRODUCTION

        The new revision starts its own governance lifecycle.
        """

        source = self.get(
            tenant_id=tenant_id,
            rule_id=rule_id,
        )

        if source is None:
            return None

        changes = payload.model_dump(
            mode="python",
            exclude_unset=True,
        )

        unknown = set(changes) - _FORKABLE_FIELDS

        if unknown:
            raise ValueError(
                f"Cannot revise fields: {sorted(unknown)}"
            )

        # Copy only approved content fields from the source.
        base = {
            field: getattr(source, field)
            for field in _FORKABLE_FIELDS
        }

        # Apply the analyst/operator's proposed changes.
        base.update(changes)

        base.update(
            status=DetectionRuleStatus.DRAFT.value,
            version=source.version + 1,
            enabled=True,
            forked_from_id=source.id,
            created_by_id=actor_id,
        )

        return self.rules.create(
            tenant_id=tenant_id,
            data=base,
        )

    def transition(
        self,
        *,
        tenant_id: UUID,
        rule_id: UUID,
        target_status: str,
        actor_id: UUID,
        notes: str | None = None,
    ):
        """Move a detection rule through its governed lifecycle.

        Lifecycle:

            DRAFT
              -> TESTING
              -> BACKTESTED
              -> CANARY
              -> APPROVED
              -> PRODUCTION
              -> MONITORED
              -> TUNED / RETIRED

        Governance checks such as peer-review and approval separation of
        duties are enforced here rather than trusting the API client.
        """

        rule = self.get(
            tenant_id=tenant_id,
            rule_id=rule_id,
        )

        if rule is None:
            return None

        try:
            target = DetectionRuleStatus(target_status)
        except ValueError as exc:
            raise ValueError(
                f"Unknown detection rule status '{target_status}'"
            ) from exc

        current = DetectionRuleStatus(rule.status)

        validation = self.validator.validate_for_transition(
            rule,
            target,
        )

        if not validation.passed:
            messages = "; ".join(
                f"[{issue.code}] {issue.message}"
                for issue in validation.errors
            )

            raise ValueError(
                "Rule failed validation for transition "
                f"'{rule.status}' -> '{target_status}': {messages}"
            )

        # Base transition update.
        data: dict = {
            "status": target_status,
        }

        if (
            current == DetectionRuleStatus.DRAFT
            and target == DetectionRuleStatus.TESTING
        ):
            # The author cannot perform their own peer review.
            if (
                rule.created_by_id is not None
                and actor_id == rule.created_by_id
            ):
                raise SeparationOfDutiesError(
                    "The rule's author cannot perform its peer review"
                )

            data.update(
                reviewed_by_id=actor_id,
                reviewed_at=datetime.now(timezone.utc),
                review_notes=notes,
            )

        if target == DetectionRuleStatus.APPROVED:
            # A rule must have completed peer review first.
            if rule.reviewed_by_id is None:
                raise ValueError(
                    "Rule cannot be approved before it has completed "
                    "peer review"
                )

            if (
                rule.created_by_id is not None
                and actor_id == rule.created_by_id
            ):
                raise SeparationOfDutiesError(
                    "The rule's author cannot approve it for production"
                )

            data.update(
                approved_by_id=actor_id,
                approved_at=datetime.now(timezone.utc),
                approval_notes=notes,
            )

        if target == DetectionRuleStatus.PRODUCTION:
            data["published_at"] = datetime.now(timezone.utc)

        updated = self.rules.update(
            tenant_id=tenant_id,
            rule_id=rule_id,
            data=data,
        )

        if (
            target == DetectionRuleStatus.PRODUCTION
            and rule.forked_from_id is not None
        ):
            parent = self.get(
                tenant_id=tenant_id,
                rule_id=rule.forked_from_id,
            )

            if (
                parent is not None
                and DetectionRuleStatus(parent.status)
                in _SUPERSEDABLE_LIVE_STATUSES
            ):
                self.rules.update(
                    tenant_id=tenant_id,
                    rule_id=parent.id,
                    data={
                        "status": DetectionRuleStatus.RETIRED.value,
                    },
                )

        return updated

    def list_production_rules(
        self,
        *,
        tenant_id: UUID,
        limit: int = 500,
        offset: int = 0,
    ):
        """Return production detection rules for a tenant."""

        return self.rules.list_production_rules(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
        )