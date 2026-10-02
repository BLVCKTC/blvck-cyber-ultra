from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.alert import Alert
from app.db.models.detection_rule import DetectionRule
from app.db.models.mitre import (
    DetectionRuleTechnique,
    MitreCampaignTechnique,
    MitreGroup,
    MitreGroupTechnique,
    MitreMitigation,
    MitreSoftware,
    MitreSoftwareTechnique,
    MitreTactic,
    MitreTechnique,
    MitreTechniqueMitigation,
    MitreTechniqueTactic,
)
from app.db.models.security_event import SecurityEvent

TECHNIQUE_CAP = 20
TOP_N = 10
DESC_MAX = 400
GUIDANCE_MAX = 600


def _trunc(value: str | None, limit: int) -> str | None:
    if value is None:
        return None
    return value if len(value) <= limit else value[:limit] + "...[truncated]"


def _dom(value: Any) -> str | None:
    # MitreDomain is a (str, Enum); str() would give "MitreDomain.X".
    return getattr(value, "value", value) if value is not None else None


def _top(names_by_tech: dict[UUID, list[str]], tid: UUID) -> dict[str, Any]:
    names = sorted(set(names_by_tech.get(tid, [])), key=str.lower)
    return {"total": len(names), "top": names[:TOP_N]}


def _collect_names(db: Session, stmt, ) -> dict[UUID, list[str]]:
    out: dict[UUID, list[str]] = {}
    for tid, name in db.execute(stmt).all():
        out.setdefault(tid, []).append(name)
    return out


def collect_mitre_context(
    db: Session,
    *,
    tenant_id: UUID,
    alert_id: UUID,
) -> dict[str, Any] | None:
    """
    Read-only MITRE ATT&CK context for one alert.

    Returns {"note": str, "data": JSON-safe dict}, or None when the alert is
    missing or belongs to another tenant. Never writes or commits.
    The detection_rule_technique bridge is authoritative; the rule's
    mitre_technique_ids array is only compared against it to flag drift.
    """
    alert = db.get(Alert, alert_id)
    if alert is None or alert.tenant_id != tenant_id:
        return None

    gaps: list[str] = []

    rule: DetectionRule | None = None
    if alert.detection_rule_id is not None:
        rule = db.get(DetectionRule, alert.detection_rule_id)
        if rule is not None and rule.tenant_id != tenant_id:
            rule = None
    if rule is None:
        gaps.append(
            "rule_missing_or_deleted"
            if alert.detection_rule_id is not None
            else "no_rule_linked"
        )

    event: SecurityEvent | None = None
    if alert.security_event_id is not None:
        event = db.get(SecurityEvent, alert.security_event_id)
        if event is not None and event.tenant_id != tenant_id:
            event = None

    # ---- Rule mapping (bridge = source of truth) ----------------------
    technique_rows: list[MitreTechnique] = []
    total_mapped = 0
    bridge_mitre_ids: set[str] = set()
    stix_only = 0
    tech_ids: list[UUID] = []

    if rule is not None:
        bridge_ids = list(
            db.execute(
                select(DetectionRuleTechnique.mitre_technique_id).where(
                    DetectionRuleTechnique.detection_rule_id == rule.id
                )
            ).scalars()
        )
        total_mapped = len(bridge_ids)

        if bridge_ids:
            all_techs = list(
                db.execute(
                    select(MitreTechnique).where(MitreTechnique.id.in_(bridge_ids))
                ).scalars()
            )
            bridge_mitre_ids = {t.mitre_id for t in all_techs if t.mitre_id}
            stix_only = sum(1 for t in all_techs if not t.mitre_id)
            all_techs.sort(key=lambda t: (t.mitre_id is None, t.mitre_id or "", t.name))
            technique_rows = all_techs[:TECHNIQUE_CAP]
            tech_ids = [t.id for t in technique_rows]
        else:
            gaps.append("rule_has_no_mitre_mapping")

        array_ids = set(rule.mitre_technique_ids or [])
        if array_ids - bridge_mitre_ids:
            gaps.append("rule_array_has_ids_missing_from_bridge")
        if bridge_mitre_ids - array_ids:
            gaps.append("bridge_has_ids_missing_from_rule_array")

    # ---- Enrichment, batched ------------------------------------------
    tactics: dict[UUID, list[dict[str, Any]]] = {}
    mitigations: dict[UUID, list[str]] = {}
    groups: dict[UUID, list[str]] = {}
    software: dict[UUID, list[str]] = {}
    campaigns: dict[UUID, int] = {}

    if tech_ids:
        for tid, tactic in db.execute(
            select(MitreTechniqueTactic.mitre_technique_id, MitreTactic).join(
                MitreTactic, MitreTactic.id == MitreTechniqueTactic.mitre_tactic_id
            ).where(MitreTechniqueTactic.mitre_technique_id.in_(tech_ids))
        ).all():
            tactics.setdefault(tid, []).append(
                {
                    "mitre_id": tactic.mitre_id,
                    "shortname": tactic.shortname,
                    "name": tactic.name,
                }
            )

        mitigations = _collect_names(
            db,
            select(MitreTechniqueMitigation.mitre_technique_id, MitreMitigation.name)
            .join(
                MitreMitigation,
                MitreMitigation.id == MitreTechniqueMitigation.mitre_mitigation_id,
            )
            .where(
                MitreTechniqueMitigation.mitre_technique_id.in_(tech_ids),
                MitreMitigation.deprecated.is_(False),
            ),
        )
        groups = _collect_names(
            db,
            select(MitreGroupTechnique.mitre_technique_id, MitreGroup.name)
            .join(MitreGroup, MitreGroup.id == MitreGroupTechnique.mitre_group_id)
            .where(
                MitreGroupTechnique.mitre_technique_id.in_(tech_ids),
                MitreGroup.deprecated.is_(False),
            ),
        )
        software = _collect_names(
            db,
            select(MitreSoftwareTechnique.mitre_technique_id, MitreSoftware.name)
            .join(
                MitreSoftware,
                MitreSoftware.id == MitreSoftwareTechnique.mitre_software_id,
            )
            .where(
                MitreSoftwareTechnique.mitre_technique_id.in_(tech_ids),
                MitreSoftware.deprecated.is_(False),
            ),
        )
        campaigns = {
            tid: n
            for tid, n in db.execute(
                select(
                    MitreCampaignTechnique.mitre_technique_id,
                    func.count(),
                )
                .where(MitreCampaignTechnique.mitre_technique_id.in_(tech_ids))
                .group_by(MitreCampaignTechnique.mitre_technique_id)
            ).all()
        }

    techniques_out = [
        {
            "mitre_id": t.mitre_id,
            "stix_id": t.stix_id,
            "name": t.name,
            "domain": _dom(t.domain),
            "is_subtechnique": t.is_subtechnique,
            "revoked": t.revoked,
            "deprecated": t.deprecated,
            "description": _trunc(t.description, DESC_MAX),
            "detection_guidance": _trunc(t.detection_guidance, GUIDANCE_MAX),
            "tactics": sorted(tactics.get(t.id, []), key=lambda x: x["shortname"]),
            "mitigations": _top(mitigations, t.id),
            "groups": _top(groups, t.id),
            "software": _top(software, t.id),
            "campaign_count": campaigns.get(t.id, 0),
        }
        for t in technique_rows
    ]

    if any(t["revoked"] or t["deprecated"] for t in techniques_out):
        gaps.append("rule_maps_to_revoked_or_deprecated_technique")
    if stix_only:
        gaps.append("rule_maps_to_technique_without_mitre_id")

    # ---- Event-asserted technique (secondary, informational) ----------
    event_technique: dict[str, Any] | None = None
    if event is not None and event.mitre_technique_id:
        matches = list(
            db.execute(
                select(MitreTechnique).where(
                    MitreTechnique.mitre_id == event.mitre_technique_id
                )
            ).scalars()
        )
        event_technique = {
            "asserted_id": event.mitre_technique_id,
            "asserted_tactic": event.mitre_tactic,
            "known_in_catalog": bool(matches),
            "domains": sorted({_dom(m.domain) for m in matches if m.domain}),
            "in_rule_mapping": event.mitre_technique_id in bridge_mitre_ids,
        }
        if not matches:
            gaps.append("event_technique_not_in_catalog")
        elif rule is not None and not event_technique["in_rule_mapping"]:
            gaps.append("event_technique_differs_from_rule_mapping")

    data: dict[str, Any] = {
        "rule_id": str(rule.id) if rule is not None else None,
        "techniques": techniques_out,
        "techniques_total": total_mapped,
        "techniques_truncated": total_mapped > TECHNIQUE_CAP,
        "event_technique": event_technique,
        "gaps": gaps,
    }

    if techniques_out:
        ids = ", ".join(t["mitre_id"] or "no-id" for t in techniques_out[:5])
        more = "" if total_mapped <= 5 else f" (+{total_mapped - 5} more)"
        note = f"rule maps to {total_mapped} technique(s): {ids}{more}"
    else:
        note = "no MITRE mapping available for this alert"
    if gaps:
        note += f"; gaps: {', '.join(gaps)}"

    return {"note": note, "data": data}