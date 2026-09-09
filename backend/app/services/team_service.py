from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.team import Team
from app.db.models.team_member import TeamMember
from app.db.repositories.membership_repo import MembershipRepo
from app.db.repositories.team_repo import TeamRepo
from app.schemas.team import TeamCreate, TeamMemberCreate, TeamMemberUpdate, TeamUpdate
from app.services.audit_service import record_audit_event

class TeamService:
    """Business logic for teams and team membership."""

    def __init__(self, db: Session):
        self.db = db
        self.teams = TeamRepo(db)
        self.memberships = MembershipRepo(db)

    def _get_required_team(self, team_id: UUID, tenant_id: UUID) -> Team:
        team = self.teams.get_by_id(team_id)
        if team is None or team.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="team_not_found")
        return team

    def _get_required_team_member(self, team: Team, membership_id: UUID) -> TeamMember:
        team_member = self.teams.get_member(team.id, membership_id)
        if team_member is None:
            raise HTTPException(status_code=404, detail="team_member_not_found")
        return team_member

    def list_teams(self, tenant_id: UUID) -> list[Team]:
        return self.teams.list_for_tenant(tenant_id)

    def get_team(self, team_id: UUID, tenant_id: UUID) -> Team:
        return self._get_required_team(team_id, tenant_id)

    def create_team(self, tenant_id: UUID, payload: TeamCreate, *, actor_user_id: UUID) -> Team:
        try:
             team = self.teams.create(tenant_id=tenant_id, name=payload.name, description=payload.description)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        record_audit_event(
            self.db, tenant_id=tenant_id, actor_user_id=actor_user_id,
            action="team.created", entity_type="team", entity_id=team.id,
            payload={"name": team.name},
        )
        return team

    def update_team(self, team_id: UUID, tenant_id: UUID, payload: TeamUpdate) -> Team:
        team = self._get_required_team(team_id, tenant_id)
        try:
            return self.teams.update(team, name=payload.name, description=payload.description)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    def delete_team(self, team_id: UUID, tenant_id: UUID, *, actor_user_id: UUID) -> None:
        team = self._get_required_team(team_id, tenant_id)
        record_audit_event(
            self.db, tenant_id=tenant_id, actor_user_id=actor_user_id,
            action="team.deleted", entity_type="team", entity_id=team.id,
            payload={"name": team.name},
        )
        self.teams.delete(team)

    def list_members(self, team_id: UUID, tenant_id: UUID) -> list[TeamMember]:
        team = self._get_required_team(team_id, tenant_id)
        return self.teams.list_members(team.id)

    def add_member(self, team_id: UUID, tenant_id: UUID, payload: TeamMemberCreate) -> TeamMember:
        team = self._get_required_team(team_id, tenant_id)

        # membership_id must belong to this same tenant — otherwise this
        # would let someone attach a different tenant's membership row.
        membership = self.memberships.get_by_id(payload.membership_id)
        if membership is None or membership.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="membership_not_found")

        try:
            return self.teams.add_member(
                team=team, membership_id=payload.membership_id, role=payload.role
            )
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    def update_member(
        self, team_id: UUID, tenant_id: UUID, membership_id: UUID, payload: TeamMemberUpdate
    ) -> TeamMember:
        team = self._get_required_team(team_id, tenant_id)
        team_member = self._get_required_team_member(team, membership_id)
        return self.teams.update_member_role(team_member, payload.role)

    def remove_member(self, team_id: UUID, tenant_id: UUID, membership_id: UUID) -> None:
        team = self._get_required_team(team_id, tenant_id)
        team_member = self._get_required_team_member(team, membership_id)
        self.teams.remove_member(team_member)