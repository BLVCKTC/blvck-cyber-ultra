"""enable row level security

Revision ID: 7937e89cd9f4
Revises: 1540f7fc462a
Create Date: 2026-08-31 09:05:49.421159

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7937e89cd9f4'
down_revision: Union[str, None] = '1540f7fc462a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Ordinary tenant-scoped tables: standard tenant_id-equality policy.
# Excludes users, tenants, pkce_attempts (no tenant_id column — not
# tenant-isolated in this sense) and memberships (handled separately below).
TENANT_TABLES = [
    "security_events",
    "detection_rules",
    "alerts",
    "investigations",
    "evidence",
    # add every new tenant-owned table here in the same migration that
    # creates it — teams, team_members, api_keys, domains, audit_log_entries,
    # rule_versions, detection_matches, incidents, etc. as each lands
]


def upgrade() -> None:
    for table in TENANT_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
        op.execute(f"""
            CREATE POLICY tenant_isolation_{table} ON {table}
            USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
        """)

    op.execute("ALTER TABLE memberships ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE memberships FORCE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS membership_visibility ON memberships")
    op.execute("""
        CREATE POLICY membership_visibility ON memberships
        USING (
            user_id = current_setting('app.user_id', true)::uuid
            OR tenant_id = current_setting('app.tenant_id', true)::uuid
        )
        WITH CHECK (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        )
    """)

def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS membership_visibility ON memberships")
    op.execute("ALTER TABLE memberships NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE memberships DISABLE ROW LEVEL SECURITY")

    for table in TENANT_TABLES:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")