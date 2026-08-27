from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permission
from app.db.models.intelligence import Asset, Indicator, Vulnerability, VulnerabilityInstance

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])


def tenant_id(membership):
    return membership.tenant_id


@router.get("/assets", dependencies=[Depends(require_permission("assets.read"))])
def list_assets(db: Session = Depends(get_db), membership=Depends(require_permission("assets.read"))):
    return db.scalars(select(Asset).where(Asset.tenant_id == tenant_id(membership)).order_by(Asset.updated_at.desc() if hasattr(Asset, "updated_at") else Asset.created_at.desc())).all()


@router.get("/vulnerabilities", dependencies=[Depends(require_permission("vulnerabilities.read"))])
def list_vulnerabilities(db: Session = Depends(get_db), membership=Depends(require_permission("vulnerabilities.read"))):
    return db.scalars(select(Vulnerability).where(Vulnerability.tenant_id == tenant_id(membership)).order_by(Vulnerability.created_at.desc())).all()


@router.get("/vulnerability-instances", dependencies=[Depends(require_permission("vulnerabilities.read"))])
def list_vulnerability_instances(db: Session = Depends(get_db), membership=Depends(require_permission("vulnerabilities.read"))):
    return db.scalars(select(VulnerabilityInstance).where(VulnerabilityInstance.tenant_id == tenant_id(membership)).order_by(VulnerabilityInstance.first_seen_at.desc())).all()


@router.get("/indicators", dependencies=[Depends(require_permission("intelligence.read"))])
def list_indicators(db: Session = Depends(get_db), membership=Depends(require_permission("intelligence.read"))):
    return db.scalars(select(Indicator).where(Indicator.tenant_id == tenant_id(membership)).order_by(Indicator.created_at.desc())).all()
