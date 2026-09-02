from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.db.models.enums import TeamMemberRole
from app.db.models.team import Team
from app.db.models.team_member import TeamMember


class TeamRepo:
    """Repository for teams and team membership."""

    def __init__(self, db: Session):
        self.db = db

    # ================= TEAMS =================

    def get_by_id(self, team_id: UUID) -> Team | None:
        return self.db.get(Team, team_id)

    def list_for_tenant(self, tenant_id: UUID) -> list[Team]:
        return list(
            self.db.scalars(
                select(Team)
                .where(Team.tenant_id == tenant_id)
                .order_by(Team.created_at)
            )
        )

    def name_exists(self, tenant_id: UUID, name: str) -> bool:
        result = self.db.scalar(
            select(exists().where(Team.tenant_id == tenant_id, Team.name == name))
        )
        return bool(result)

    def create(self, *, tenant_id: UUID, name: str, description: str | None) -> Team:
        if self.name_exists(tenant_id, name):
            raise ValueError("A team with this name already exists.")

        team = Team(tenant_id=tenant_id, name=name, description=description)
        self.db.add(team)
        self.db.commit()
        self.db.refresh(team)
        return team

    def update(self, team: Team, *, name: str | None, description: str | None) -> Team:
        if name is not None and name != team.name:
            if self.name_exists(team.tenant_id, name):
                raise ValueError("A team with this name already exists.")
            team.name = name

        if description is not None:
            team.description = description

        self.db.commit()
        self.db.refresh(team)
        return team

    def delete(self, team: Team) -> None:
        self.db.delete(team)
        self.db.commit()

    # ================= TEAM MEMBERS =================

    def get_member(self, team_id: UUID, membership_id: UUID) -> TeamMember | None:
        return self.db.scalar(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.membership_id == membership_id,
            )
        )

    def list_members(self, team_id: UUID) -> list[TeamMember]:
        return list(
            self.db.scalars(
                select(TeamMember)
                .where(TeamMember.team_id == team_id)
                .order_by(TeamMember.created_at)
            )
        )

    def add_member(
        self,
        *,
        team: Team,
        membership_id: UUID,
        role: TeamMemberRole = TeamMemberRole.MEMBER,
    ) -> TeamMember:
        if self.get_member(team.id, membership_id) is not None:
            raise ValueError("This member already belongs to the team.")

        team_member = TeamMember(
            team_id=team.id,
            membership_id=membership_id,
            tenant_id=team.tenant_id,
            role=role,
        )
        self.db.add(team_member)
        self.db.commit()
        self.db.refresh(team_member)
        return team_member

    def update_member_role(self, team_member: TeamMember, role: TeamMemberRole) -> TeamMember:
        team_member.role = role
        self.db.commit()
        self.db.refresh(team_member)
        return team_member

    def remove_member(self, team_member: TeamMember) -> None:
        self.db.delete(team_member)
        self.db.commit()