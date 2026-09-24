# app/api/routes/investigations.py

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_active_membership,
    get_db,
    require_permission,
)
from app.db.models.membership import Membership
from app.schemas.investigation import (
    EvidenceCreate,
    EvidenceRead,
    InvestigationCreate,
    InvestigationRead,
    InvestigationUpdate,
)
from app.services.investigation_orchestrator_service import (
    InvestigationOrchestratorService,
    OrchestrationError,
)
from app.services.investigation_service import InvestigationService


router = APIRouter(
    prefix="/investigations",
    tags=["Investigations"],
)


def get_investigation_service(
    db: Session = Depends(get_db),
) -> InvestigationService:
    """Create an investigation service using the current database session."""
    return InvestigationService(db)


def get_investigation_orchestrator_service(
    db: Session = Depends(get_db),
) -> InvestigationOrchestratorService:
    """Create an investigation orchestrator using the current database session."""
    return InvestigationOrchestratorService(db)


@router.post(
    "",
    response_model=InvestigationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("forensics.manage")),
    ],
)
def create_investigation(
    payload: InvestigationCreate,
    membership: Membership = Depends(get_active_membership),
    service: InvestigationService = Depends(get_investigation_service),
) -> InvestigationRead:
    return service.create(
        membership.tenant_id,
        payload,
    )


@router.get(
    "",
    response_model=list[InvestigationRead],
    dependencies=[
        Depends(require_permission("forensics.view")),
    ],
)
def list_investigations(
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter investigations by status.",
    ),
    alert_id: UUID | None = Query(
        default=None,
        description="Filter investigations associated with an alert.",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of investigations to return.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of investigations to skip.",
    ),
    membership: Membership = Depends(get_active_membership),
    service: InvestigationService = Depends(get_investigation_service),
) -> list[InvestigationRead]:
    return service.list(
        membership.tenant_id,
        status=status_filter,
        alert_id=alert_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/orchestrate/{alert_id}",
    dependencies=[
        Depends(require_permission("ai.assistant.use")),
    ],
)
def orchestrate_investigation(
    alert_id: UUID,
    membership: Membership = Depends(get_active_membership),
    orchestrator: InvestigationOrchestratorService = Depends(
        get_investigation_orchestrator_service,
    ),
) -> dict[str, Any]:
    """
    Run the investigation orchestrator for an alert.

    This is intentionally an explicit synchronous endpoint. It should not be
    called from alert ingestion until orchestration is moved to a background
    worker or durable queue.
    """
    try:
        result = orchestrator.run_for_alert(
            tenant_id=membership.tenant_id,
            alert_id=alert_id,
        )
    except OrchestrationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return {
        "investigation_id": result.get("investigation_id"),
        "run_id": result.get("run_id"),
        "completed_steps": result.get("completed_steps", []),
        "findings": result.get("findings", {}),
    }


@router.get(
    "/{investigation_id}",
    response_model=InvestigationRead,
    dependencies=[
        Depends(require_permission("forensics.view")),
    ],
)
def get_investigation(
    investigation_id: UUID,
    membership: Membership = Depends(get_active_membership),
    service: InvestigationService = Depends(get_investigation_service),
) -> InvestigationRead:
    investigation = service.get(
        membership.tenant_id,
        investigation_id,
    )

    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found.",
        )

    return investigation


@router.patch(
    "/{investigation_id}",
    response_model=InvestigationRead,
    dependencies=[
        Depends(require_permission("forensics.manage")),
    ],
)
def update_investigation(
    investigation_id: UUID,
    payload: InvestigationUpdate,
    membership: Membership = Depends(get_active_membership),
    service: InvestigationService = Depends(get_investigation_service),
) -> InvestigationRead:
    investigation = service.update(
        membership.tenant_id,
        investigation_id,
        payload,
    )

    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found.",
        )

    return investigation


@router.get(
    "/{investigation_id}/evidence",
    response_model=list[EvidenceRead],
    dependencies=[
        Depends(require_permission("forensics.view")),
    ],
)
def list_evidence(
    investigation_id: UUID,
    membership: Membership = Depends(get_active_membership),
    service: InvestigationService = Depends(get_investigation_service),
) -> list[EvidenceRead]:
    investigation = service.get(
        membership.tenant_id,
        investigation_id,
    )

    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found.",
        )

    return service.evidence(
        membership.tenant_id,
        investigation_id,
    )


@router.post(
    "/{investigation_id}/evidence",
    response_model=EvidenceRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("forensics.manage")),
    ],
)
def add_evidence(
    investigation_id: UUID,
    payload: EvidenceCreate,
    membership: Membership = Depends(get_active_membership),
    service: InvestigationService = Depends(get_investigation_service),
) -> EvidenceRead:
    evidence = service.add_evidence(
        membership.tenant_id,
        investigation_id,
        payload,
    )

    if evidence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found.",
        )

    return evidence
