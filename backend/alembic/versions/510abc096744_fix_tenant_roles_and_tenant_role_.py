"""fix tenant_roles and tenant_role_permissions rls for cross-tenant permission listing

Revision ID: 510abc096744
Revises: 61338bb0b6d7
Create Date: 2026-09-03 10:24:19.677150

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '510abc096744'
down_revision: Union[str, None] = '61338bb0b6d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_tenant_roles ON tenant_roles")
    op.execute("""
        CREATE POLICY tenant_isolation_tenant_roles ON tenant_roles
        USING (
            tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
            OR tenant_id IN (
                SELECT tenant_id FROM memberships
                WHERE user_id = NULLIF(current_setting('app.user_id', true), '')::uuid
            )
        )
        WITH CHECK (
            tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        )
    """)

    op.execute("DROP POLICY IF EXISTS tenant_isolation_tenant_role_permissions ON tenant_role_permissions")
    op.execute("""
        CREATE POLICY tenant_isolation_tenant_role_permissions ON tenant_role_permissions
        USING (
            tenant_role_id IN (
                SELECT id FROM tenant_roles
                WHERE tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
                   OR tenant_id IN (
                        SELECT tenant_id FROM memberships
                        WHERE user_id = NULLIF(current_setting('app.user_id', true), '')::uuid
                   )
            )
        )
        WITH CHECK (
            tenant_role_id IN (
                SELECT id FROM tenant_roles
                WHERE tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
            )
        )
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_tenant_role_permissions ON tenant_role_permissions")
    op.execute("""
        CREATE POLICY tenant_isolation_tenant_role_permissions ON tenant_role_permissions
        USING (
            tenant_role_id IN (
                SELECT id FROM tenant_roles
                WHERE tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
            )
        )
        WITH CHECK (
            tenant_role_id IN (
                SELECT id FROM tenant_roles
                WHERE tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
            )
        )
    """)

    op.execute("DROP POLICY IF EXISTS tenant_isolation_tenant_roles ON tenant_roles")
    op.execute("""
        CREATE POLICY tenant_isolation_tenant_roles ON tenant_roles
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)