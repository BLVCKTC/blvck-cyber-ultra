from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.detection_rule import (
    DetectionRule,
    DetectionRuleStatus,
)
from app.db.repositories.detection_rule_repo import DetectionRuleRepository
from app.db.repositories.mitre_repo import MitreRepo
from app.services.detection_rules.validation import (
    RuleValidator,
    ValidationIssue,
    ValidationSeverity,
)


class SeparationOfDutiesError(ValueError):
    pass


class RuleLockedError(ValueError):
    pass


class RuleValidationError(ValueError):
    def __init__(
        self,
        message: str,
        issues: list[ValidationIssue],
    ) -> None:
        super().__init__(message)
        self.issues = issues


@dataclass(slots=True)
class RuleTransitionResult:
    rule: DetectionRule
    warnings: list[ValidationIssue]


_LOCKED_FOR_DIRECT_EDIT = {
    DetectionRuleStatus.TESTING,
    DetectionRuleStatus.BACKTESTED,
    DetectionRuleStatus.CANARY,
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


_ALLOWED_TRANSITIONS: dict[
    DetectionRuleStatus,
    set[DetectionRuleStatus],
] = {
    DetectionRuleStatus.DRAFT: {
        DetectionRuleStatus.TESTING,
        DetectionRuleStatus.RETIRED,
    },
    DetectionRuleStatus.TESTING: {
        DetectionRuleStatus.BACKTESTED,
        DetectionRuleStatus.RETIRED,
    },
    DetectionRuleStatus.BACKTESTED: {
        DetectionRuleStatus.CANARY,
        DetectionRuleStatus.RETIRED,
    },
    DetectionRuleStatus.CANARY: {
        DetectionRuleStatus.APPROVED,
        DetectionRuleStatus.RETIRED,
    },
    DetectionRuleStatus.APPROVED: {
        DetectionRuleStatus.PRODUCTION,
        DetectionRuleStatus.RETIRED,
    },
    DetectionRuleStatus.PRODUCTION: {
        DetectionRuleStatus.MONITORED,
        DetectionRuleStatus.RETIRED,
    },
    DetectionRuleStatus.MONITORED: {
        DetectionRuleStatus.TUNED,
        DetectionRuleStatus.RETIRED,
    },
    DetectionRuleStatus.TUNED: {
        DetectionRuleStatus.RETIRED,
    },
    DetectionRuleStatus.RETIRED: set(),
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


_UPDATABLE_FIELDS = (
    _FORKABLE_FIELDS | {"enabled"}
) - {"mitre_technique_ids"}


_RELATIONSHIP_FIELDS = {
    "mitre_technique_ids",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DetectionRuleService:
    def __init__(
        self,
        db: Session | None = None,
        rules: DetectionRuleRepository | None = None,
        mitre_repo: MitreRepo | None = None,
        validator: RuleValidator | None = None,
    ) -> None:
        self.db = db

        if rules is None:
            if db is None:
                raise ValueError("Either db or rules must be provided")
            rules = DetectionRuleRepository(db)

        if mitre_repo is None:
            if db is None:
                raise ValueError("Either db or mitre_repo must be provided")
            mitre_repo = MitreRepo(db)

        self.rules = rules
        self.mitre_repo = mitre_repo
        self.validator = validator or RuleValidator()

    def create(
        self,
        *,
        tenant_id: UUID,
        payload: Any | None = None,
        data: dict[str, Any] | None = None,
        actor_id: UUID | None = None,
    ) -> DetectionRule:
        if payload is not None:
            if isinstance(payload, dict):
                rule_data = dict(payload)
            else:
                rule_data = payload.model_dump(exclude_unset=True)
        elif data is not None:
            rule_data = dict(data)
        else:
            raise ValueError("Either payload or data must be provided")

        rule_data.pop("tenant_id", None)

        if actor_id is not None:
            rule_data.setdefault("created_by_id", actor_id)

        rule_data.setdefault(
            "status",
            DetectionRuleStatus.DRAFT.value,
        )

        rule = self.rules.create(
            tenant_id=tenant_id,
            data=rule_data,
        )

        return rule

    def get(
        self,
        *,
        tenant_id: UUID,
        rule_id: UUID,
    ) -> DetectionRule | None:
        return self.rules.get(
            tenant_id=tenant_id,
            rule_id=rule_id,
        )

    def list(
        self,
        *,
        tenant_id: UUID,
        status: DetectionRuleStatus | None = None,
        enabled: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DetectionRule]:
        return self.rules.list(
            tenant_id=tenant_id,
            status=status,
            enabled=enabled,
            limit=limit,
            offset=offset,
        )

    def ensure_editable(
        self,
        rule: DetectionRule,
    ) -> None:
        status = self._status(rule)

        if status != DetectionRuleStatus.DRAFT:
            raise RuleLockedError(
                f"Rule '{rule.id}' is locked because it is "
                f"in '{status.value}' status. Create a revision "
                f"before making changes."
            )

    def update(
        self,
        *,
        tenant_id: UUID,
        rule_id: UUID,
        data: dict[str, Any],
        actor_id: UUID | None = None,
    ) -> DetectionRule | None:
        rule = self.get(
            tenant_id=tenant_id,
            rule_id=rule_id,
        )

        if rule is None:
            return None

        self.ensure_editable(rule)
        self._validate_update_fields(data)

        payload = dict(data)

        if actor_id is not None:
            payload["updated_by_id"] = actor_id

        return self.rules.update(
            tenant_id=tenant_id,
            rule_id=rule_id,
            data=payload,
        )

    def delete(
        self,
        *,
        tenant_id: UUID,
        rule_id: UUID,
    ) -> bool:
        rule = self.get(
            tenant_id=tenant_id,
            rule_id=rule_id,
        )

        if rule is None:
            return False

        self.ensure_editable(rule)

        return self.rules.delete(
            tenant_id=tenant_id,
            rule_id=rule_id,
        )

    def propose_revision(
        self,
        *,
        tenant_id: UUID,
        source_rule_id: UUID,
        actor_id: UUID,
        overrides: dict[str, Any] | None = None,
    ) -> DetectionRule:
        source = self.get(
            tenant_id=tenant_id,
            rule_id=source_rule_id,
        )

        if source is None:
            raise ValueError("Source detection rule not found")

        source_status = self._status(source)

        if source_status not in _LOCKED_FOR_DIRECT_EDIT:
            raise RuleLockedError(
                f"Rule '{source.id}' is not in a revision-eligible "
                f"locked state."
            )

        data = self._build_revision_data(
            source=source,
            overrides=overrides or {},
            actor_id=actor_id,
        )

        source_techniques = self.mitre_repo.list_techniques_for_rule(
            source.id
        )

        data["mitre_technique_ids"] = [
            technique.mitre_id
            for technique in source_techniques
            if technique.mitre_id
        ]

        revision = self.rules.create(
            tenant_id=tenant_id,
            data=data,
        )

        self.mitre_repo.copy_rule_techniques(
            source_rule_id=source.id,
            target_rule_id=revision.id,
            created_by=actor_id,
        )

        return revision

    def transition(
        self,
        *,
        tenant_id: UUID,
        rule_id: UUID,
        target_status: DetectionRuleStatus | str,
        actor_id: UUID,
        notes: str | None = None,
        review_notes: str | None = None,
        approval_notes: str | None = None,
    ) -> RuleTransitionResult | None:
        rule = self.get(
            tenant_id=tenant_id,
            rule_id=rule_id,
        )

        if rule is None:
            return None

        current = self._status(rule)
        target = self._parse_status(target_status)

        self._validate_transition(
            current=current,
            target=target,
        )

        validation = self.validator.validate_for_transition(
            rule,
            target,
        )

        if not validation.passed:
            message = "; ".join(
                f"[{issue.code}] {issue.message}"
                for issue in validation.errors
            )
            raise RuleValidationError(
                f"Rule failed validation for transition "
                f"'{current.value}' -> '{target.value}': {message}",
                issues=validation.errors,
            )

        self._enforce_separation_of_duties(
            rule=rule,
            current=current,
            target=target,
            actor_id=actor_id,
        )

        now = _utcnow()

        data: dict[str, Any] = {
            "status": target.value,
        }

        if target == DetectionRuleStatus.TESTING:
            data["reviewed_by_id"] = actor_id
            data["reviewed_at"] = now
            data["review_notes"] = (
                review_notes if review_notes is not None else notes
            )
        if target == DetectionRuleStatus.CANARY:
            data["canary_started_at"] = now
            
        if target == DetectionRuleStatus.APPROVED:
            data["approved_by_id"] = actor_id
            data["approved_at"] = now
            data["approval_notes"] = (
                approval_notes if approval_notes is not None else notes
            )

        if target == DetectionRuleStatus.PRODUCTION:
            data["published_at"] = now

        updated = self.rules.update(
            tenant_id=tenant_id,
            rule_id=rule_id,
            data=data,
        )

        if updated is None:
            return None

        if target == DetectionRuleStatus.PRODUCTION:
            self._retire_superseded_parent(
                tenant_id=tenant_id,
                rule=updated,
            )

        return RuleTransitionResult(
            rule=updated,
            warnings=validation.warnings,
        )

    def list_production_rules(
        self,
        *,
        tenant_id: UUID,
    ) -> list[DetectionRule]:
        return self.rules.list(
            tenant_id=tenant_id,
            status=DetectionRuleStatus.PRODUCTION,
            enabled=True,
        )

    @staticmethod
    def _status(rule: DetectionRule) -> DetectionRuleStatus:
        status = getattr(rule, "status", None)

        if isinstance(status, DetectionRuleStatus):
            return status

        return DetectionRuleStatus(status)

    @staticmethod
    def _parse_status(
        status: DetectionRuleStatus | str,
    ) -> DetectionRuleStatus:
        if isinstance(status, DetectionRuleStatus):
            return status

        return DetectionRuleStatus(status)

    @staticmethod
    def _validate_update_fields(
        data: dict[str, Any],
    ) -> None:
        unknown = set(data) - _UPDATABLE_FIELDS

        if unknown:
            fields = ", ".join(sorted(unknown))
            raise ValueError(
                f"Fields cannot be updated directly: {fields}"
            )

    @staticmethod
    def _validate_transition(
        *,
        current: DetectionRuleStatus,
        target: DetectionRuleStatus,
    ) -> None:
        if current == target:
            raise ValueError(
                f"Rule is already in '{current.value}' status"
            )

        allowed_targets = _ALLOWED_TRANSITIONS.get(
            current,
            set(),
        )

        if target not in allowed_targets:
            issue = ValidationIssue(
                code="invalid_transition",
                message=(
                    f"Invalid detection rule transition: "
                    f"'{current.value}' -> '{target.value}'"
                ),
                severity=ValidationSeverity.ERROR,
                field="status",
            )

            raise RuleValidationError(
                issue.message,
                issues=[issue],
            )

    @staticmethod
    def _enforce_separation_of_duties(
        *,
        rule: DetectionRule,
        current: DetectionRuleStatus,
        target: DetectionRuleStatus,
        actor_id: UUID,
    ) -> None:
        if (
            current == DetectionRuleStatus.DRAFT
            and target == DetectionRuleStatus.TESTING
            and rule.created_by_id is not None
            and actor_id == rule.created_by_id
        ):
            raise SeparationOfDutiesError(
                "The rule author cannot perform peer review"
            )

        if target == DetectionRuleStatus.APPROVED:
            if rule.reviewed_by_id is None:
                raise ValueError(
                    "The rule must complete peer review before approval"
                )

            if (
                rule.created_by_id is not None
                and actor_id == rule.created_by_id
            ):
                raise SeparationOfDutiesError(
                    "The rule author cannot approve the rule"
                )

    @staticmethod
    def _build_revision_data(
        *,
        source: DetectionRule,
        overrides: dict[str, Any],
        actor_id: UUID,
    ) -> dict[str, Any]:
        invalid = set(overrides) - _FORKABLE_FIELDS

        if invalid:
            fields = ", ".join(sorted(invalid))
            raise ValueError(
                f"Fields cannot be overridden in a revision: {fields}"
            )

        data: dict[str, Any] = {
            "name": source.name,
            "description": source.description,
            "rule_type": source.rule_type,
            "severity": source.severity,
            "query": source.query,
            "configuration": source.configuration,
            "tags": source.tags,
            "mitre_technique_ids": source.mitre_technique_ids,
            "mitre_tactic_ids": source.mitre_tactic_ids,
            "author": source.author,
            "source": source.source,
            "status": DetectionRuleStatus.DRAFT.value,
            "enabled": False,
            "created_by_id": actor_id,
            "forked_from_id": source.id,
        }

        data.update(overrides)

        data["status"] = DetectionRuleStatus.DRAFT.value
        data["enabled"] = False
        data["created_by_id"] = actor_id
        data["forked_from_id"] = source.id

        return data

    def _retire_superseded_parent(
        self,
        *,
        tenant_id: UUID,
        rule: DetectionRule,
    ) -> None:
        parent_id = getattr(rule, "forked_from_id", None)

        if parent_id is None:
            return

        parent = self.get(
            tenant_id=tenant_id,
            rule_id=parent_id,
        )

        if parent is None:
            return

        parent_status = self._status(parent)

        if parent_status not in _SUPERSEDABLE_LIVE_STATUSES:
            return

        self.rules.update(
            tenant_id=tenant_id,
            rule_id=parent.id,
            data={
                "status": DetectionRuleStatus.RETIRED.value,
                "enabled": False,
            },
        )