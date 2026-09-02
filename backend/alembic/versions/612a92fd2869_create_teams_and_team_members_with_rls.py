"""create teams and team_members with RLS

Revision ID: 612a92fd2869
Revises: 0e631fc99f76
Create Date: 2026-08-31 10:23:52.802971

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = '612a92fd2869'
down_revision: Union[str, None] = '0e631fc99f76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_teams_tenant_id", "teams", ["tenant_id"])
    op.create_index("ix_team_tenant_name", "teams", ["tenant_id", "name"], unique=True)

    team_member_role = postgresql.ENUM("lead", "member", name="teammemberrole", create_type=False,)
    team_member_role.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "team_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("team_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("membership_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("memberships.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", team_member_role, nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_team_members_team_id", "team_members", ["team_id"])
    op.create_index("ix_team_members_membership_id", "team_members", ["membership_id"])
    op.create_index("ix_team_members_tenant_id", "team_members", ["tenant_id"])
    op.create_index("ix_team_member_team_membership", "team_members",
                     ["team_id", "membership_id"], unique=True)

    # RLS — same pattern as the earlier migration, idempotent via DROP IF EXISTS
    for table in ("teams", "team_members"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
        op.execute(f"""
            CREATE POLICY tenant_isolation_{table} ON {table}
            USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
        """)


def downgrade() -> None:
    for table in ("teams", "team_members"):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.drop_table("team_members")
    op.drop_table("teams")

    team_member_role = postgresql.ENUM("lead", "member", name="teammemberrole")
    team_member_role.drop(op.get_bind(), checkfirst=True)