from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_membership, get_db, require_roles
from app.db.models.enums import MembershipRole
from app.schemas.team import (
    TeamCreate,
    TeamListResponse,
    TeamMemberCreate,
    TeamMemberListResponse,
    TeamMemberResponse,
    TeamMemberUpdate,
    TeamResponse,
    TeamUpdate,
)
from app.services.team_service import TeamService

router = APIRouter(prefix="", tags=["Teams"])


def _assert_tenant_matches(membership, tenant_id: str) -> None:
    if str(membership.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="tenant_mismatch")


def service(db: Session = Depends(get_db)) -> TeamService:
    return TeamService(db)


@router.get("/tenants/{tenant_id}/teams", response_model=TeamListResponse)
def list_teams(
    tenant_id: str = Path(..., min_length=1),
    membership=Depends(get_active_membership),
    svc: TeamService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    items = svc.list_teams(UUID(tenant_id))
    return {"items": items, "total": len(items)}


@router.post("/tenants/{tenant_id}/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreate,
    tenant_id: str = Path(..., min_length=1),
    membership=Depends(require_roles([MembershipRole.OWNER, MembershipRole.ADMIN])),
    svc: TeamService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    return svc.create_team(UUID(tenant_id), payload)


@router.get("/tenants/{tenant_id}/teams/{team_id}", response_model=TeamResponse)
def get_team(
    tenant_id: str = Path(..., min_length=1),
    team_id: UUID = Path(...),
    membership=Depends(get_active_membership),
    svc: TeamService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    return svc.get_team(team_id, UUID(tenant_id))


@router.patch("/tenants/{tenant_id}/teams/{team_id}", response_model=TeamResponse)
def update_team(
    payload: TeamUpdate,
    tenant_id: str = Path(..., min_length=1),
    team_id: UUID = Path(...),
    membership=Depends(require_roles([MembershipRole.OWNER, MembershipRole.ADMIN])),
    svc: TeamService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    return svc.update_team(team_id, UUID(tenant_id), payload)


@router.delete("/tenants/{tenant_id}/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    tenant_id: str = Path(..., min_length=1),
    team_id: UUID = Path(...),
    membership=Depends(require_roles([MembershipRole.OWNER, MembershipRole.ADMIN])),
    svc: TeamService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    svc.delete_team(team_id, UUID(tenant_id))
    return None


@router.get("/tenants/{tenant_id}/teams/{team_id}/members", response_model=TeamMemberListResponse)
def list_team_members(
    tenant_id: str = Path(..., min_length=1),
    team_id: UUID = Path(...),
    membership=Depends(get_active_membership),
    svc: TeamService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    items = svc.list_members(team_id, UUID(tenant_id))
    return {"items": items, "total": len(items)}


@router.post(
    "/tenants/{tenant_id}/teams/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_team_member(
    payload: TeamMemberCreate,
    tenant_id: str = Path(..., min_length=1),
    team_id: UUID = Path(...),
    membership=Depends(require_roles([MembershipRole.OWNER, MembershipRole.ADMIN])),
    svc: TeamService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    return svc.add_member(team_id, UUID(tenant_id), payload)


@router.patch(
    "/tenants/{tenant_id}/teams/{team_id}/members/{membership_id}",
    response_model=TeamMemberResponse,
)
def update_team_member(
    payload: TeamMemberUpdate,
    tenant_id: str = Path(..., min_length=1),
    team_id: UUID = Path(...),
    membership_id: UUID = Path(...),
    membership=Depends(require_roles([MembershipRole.OWNER, MembershipRole.ADMIN])),
    svc: TeamService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    return svc.update_member(team_id, UUID(tenant_id), membership_id, payload)


@router.delete(
    "/tenants/{tenant_id}/teams/{team_id}/members/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_team_member(
    tenant_id: str = Path(..., min_length=1),
    team_id: UUID = Path(...),
    membership_id: UUID = Path(...),
    membership=Depends(require_roles([MembershipRole.OWNER, MembershipRole.ADMIN])),
    svc: TeamService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    svc.remove_member(team_id, UUID(tenant_id), membership_id)
    return None