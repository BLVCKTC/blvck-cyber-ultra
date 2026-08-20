"""allow tenant-less PKCE login attempts

Revision ID: c4f8a1d2e9b0
Revises: 7945f6a02600
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c4f8a1d2e9b0"
down_revision: Union[str, None] = "7945f6a02600"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "pkce_attempts",
        "tenant_id",
        existing_type=sa.UUID(),
        nullable=True,
    )
    op.drop_constraint(
        "pkce_attempts_tenant_id_fkey",
        "pkce_attempts",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "pkce_attempts_tenant_id_fkey",
        "pkce_attempts",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "pkce_attempts_tenant_id_fkey",
        "pkce_attempts",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "pkce_attempts_tenant_id_fkey",
        "pkce_attempts",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "pkce_attempts",
        "tenant_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
