"""
MITRE reference-data routes.

NOTE on the sync trigger endpoint's access control: this repo's existing
permission model (MembershipRole, "platform.all", etc.) is entirely
tenant-scoped per the quarantine-endpoint finding earlier in this build —
there is currently no cross-tenant platform-admin primitive to gate a
global operation like "re-sync the MITRE reference tables" against.
Wiring `require_platform_admin` below to something real is blocked on
that same platform-admin primitive (is_platform_admin column vs. Keycloak
realm role — still undecided). Until that exists, treat this route as
NOT SAFE to expose publicly; run the sync via the `scripts/` CLI pattern
this repo already uses (see scripts/seed_database.py for the pattern)
instead of over HTTP, or gate it behind a network-level control
(internal-only route, ops VPN) rather than app-level RBAC.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_membership, get_db, require_permission
from app.db.models.membership import Membership
from app.db.models.mitre import MitreDomain
from app.db.repositories.mitre_repo import MitreRepo
from app.schemas.mitre import (
    DetectionRuleTechniqueLinkIn,
    MitreCoverageItemOut,
    MitreCoverageOut,
    MitreSyncLogOut,
    MitreTacticOut,
    MitreTechniqueOut,
)
from app.services.detection_rule_service import (
    DetectionRuleService,
    RuleLockedError,
)
from app.services.mitre_sync_service import MitreSyncService

router = APIRouter(prefix="/v1/mitre", tags=["mitre"])


@router.get("/tactics", response_model=list[MitreTacticOut])
def list_tactics(
    domain: MitreDomain = MitreDomain.ENTERPRISE,
    db: Session = Depends(get_db),
):
    return MitreRepo(db).list_tactics(domain)


@router.get("/techniques", response_model=list[MitreTechniqueOut])
def list_techniques(
    domain: MitreDomain = MitreDomain.ENTERPRISE,
    include_subtechniques: bool = True,
    db: Session = Depends(get_db),
):
    return MitreRepo(db).list_techniques(
        domain,
        include_subtechniques=include_subtechniques,
    )


@router.get("/sync-log", response_model=list[MitreSyncLogOut])
def sync_history(
    domain: MitreDomain = MitreDomain.ENTERPRISE,
    db: Session = Depends(get_db),
):
    return MitreRepo(db).sync_history(domain)


@router.post(
    "/sync/{domain}",
    response_model=MitreSyncLogOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def trigger_sync(
    domain: MitreDomain,
    db: Session = Depends(get_db),
):
    if domain == MitreDomain.MOBILE:
        raise HTTPException(
            status_code=400,
            detail="Mobile ATT&CK sync not yet implemented",
        )

    service = MitreSyncService(db)

    try:
        return service.sync_domain(domain)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"MITRE sync failed: {exc}",
        ) from exc


@router.get(
    "/detection-rules/{detection_rule_id}/techniques",
    response_model=list[MitreTechniqueOut],
    dependencies=[Depends(require_permission("detections.view"))],
)
def list_rule_techniques(
    detection_rule_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return MitreRepo(db).list_techniques_for_rule(detection_rule_id)


@router.post(
    "/detection-rules/{detection_rule_id}/techniques",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("detections.update"))],
)
def link_rule_technique(
    detection_rule_id: uuid.UUID,
    payload: DetectionRuleTechniqueLinkIn,
    membership: Membership = Depends(get_active_membership),
    db: Session = Depends(get_db),
):
    svc = DetectionRuleService(db)
    rule = svc.get(
        tenant_id=membership.tenant_id,
        rule_id=detection_rule_id,
    )

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection rule not found.",
        )

    try:
        svc.ensure_editable(rule)
    except RuleLockedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    repo = MitreRepo(db)

    technique = repo.get_technique_by_id(payload.mitre_technique_id)

    if not technique:
        raise HTTPException(
            status_code=404,
            detail="Unknown MITRE technique id",
        )

    link = repo.link_rule_to_technique(
        detection_rule_id=rule.id,
        mitre_technique_id=payload.mitre_technique_id,
        created_by=membership.user_id,
    )

    if (
        technique.mitre_id
        and technique.mitre_id not in (rule.mitre_technique_ids or [])
    ):
        rule.mitre_technique_ids = [
            *(rule.mitre_technique_ids or []),
            technique.mitre_id,
        ]
        db.commit()

    return {
        "id": link.id,
        "detection_rule_id": link.detection_rule_id,
        "mitre_technique_id": link.mitre_technique_id,
    }


@router.delete(
    "/detection-rules/{detection_rule_id}/techniques/{mitre_technique_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("detections.update"))],
)
def unlink_rule_technique(
    detection_rule_id: uuid.UUID,
    mitre_technique_id: uuid.UUID,
    membership: Membership = Depends(get_active_membership),
    db: Session = Depends(get_db),
):
    svc = DetectionRuleService(db)
    rule = svc.get(
        tenant_id=membership.tenant_id,
        rule_id=detection_rule_id,
    )

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection rule not found.",
        )

    try:
        svc.ensure_editable(rule)
    except RuleLockedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    repo = MitreRepo(db)
    technique = repo.get_technique_by_id(mitre_technique_id)

    removed = repo.unlink_rule_from_technique(
        rule.id,
        mitre_technique_id,
    )

    if not removed:
        raise HTTPException(
            status_code=404,
            detail="No such technique link",
        )

    if (
        technique
        and technique.mitre_id
        and technique.mitre_id in (rule.mitre_technique_ids or [])
    ):
        rule.mitre_technique_ids = [
            t
            for t in rule.mitre_technique_ids
            if t != technique.mitre_id
        ]
        db.commit()


@router.get(
    "/coverage",
    response_model=MitreCoverageOut,
    dependencies=[Depends(require_permission("detections.view"))],
)
def coverage(
    domain: MitreDomain = MitreDomain.ENTERPRISE,
    include_subtechniques: bool = True,
    membership: Membership = Depends(get_active_membership),
    db: Session = Depends(get_db),
):
    rows = MitreRepo(db).technique_coverage(
        tenant_id=membership.tenant_id,
        domain=domain,
        include_subtechniques=include_subtechniques,
    )

    items = [
        MitreCoverageItemOut(
            technique=MitreTechniqueOut.model_validate(row["technique"]),
            covering_rule_count=row["covering_rule_count"],
            covered=row["covered"],
        )
        for row in rows
    ]

    covered_count = sum(1 for item in items if item.covered)
    total = len(items)

    return MitreCoverageOut(
        domain=domain,
        items=items,
        total_techniques=total,
        covered_count=covered_count,
        uncovered_count=total - covered_count,
        coverage_percent=round(
            (covered_count / total * 100),
            2,
        ) if total else 0.0,
    )
