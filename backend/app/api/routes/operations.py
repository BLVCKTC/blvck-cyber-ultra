from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_active_membership, get_db, require_permission
from app.db.models.operations import AlertFeedback, DetectionMatch, ResponseAction, RuleVersion

router = APIRouter(prefix="/operations", tags=["Security Operations"])


def _tenant(membership):
    return membership.tenant_id


@router.get("/rule-versions", dependencies=[Depends(require_permission("detection_rules.read"))])
def list_rule_versions(db: Session = Depends(get_db), membership=Depends(get_active_membership)):
    return db.scalars(select(RuleVersion).where(RuleVersion.tenant_id == _tenant(membership)).order_by(RuleVersion.created_at.desc())).all()


@router.get("/detection-matches", dependencies=[Depends(require_permission("security_events.read"))])
def list_detection_matches(db: Session = Depends(get_db), membership=Depends(get_active_membership)):
    return db.scalars(select(DetectionMatch).where(DetectionMatch.tenant_id == _tenant(membership)).order_by(DetectionMatch.matched_at.desc())).all()


@router.get("/alert-feedback", dependencies=[Depends(require_permission("alerts.read"))])
def list_alert_feedback(db: Session = Depends(get_db), membership=Depends(get_active_membership)):
    return db.scalars(select(AlertFeedback).where(AlertFeedback.tenant_id == _tenant(membership)).order_by(AlertFeedback.created_at.desc())).all()


@router.get("/response-actions", dependencies=[Depends(require_permission("incidents.read"))])
def list_response_actions(db: Session = Depends(get_db), membership=Depends(get_active_membership)):
    return db.scalars(select(ResponseAction).where(ResponseAction.tenant_id == _tenant(membership)).order_by(ResponseAction.created_at.desc())).all()
