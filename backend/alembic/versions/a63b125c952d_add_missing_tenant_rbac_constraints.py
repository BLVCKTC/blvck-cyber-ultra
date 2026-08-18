"""add missing tenant RBAC constraints

Revision ID: a63b125c952d
Revises: 54808cd1f83d
Create Date: 2026-08-18 16:17:00.132813

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a63b125c952d"
down_revision: Union[str, None] = "54808cd1f83d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # memberships
    # ---------------------------------------------------------
    # Enforce one membership per user per tenant.
    op.create_index(
        "ix_membership_user_tenant",
        "memberships",
        ["user_id", "tenant_id"],
        unique=True,
    )

    # ---------------------------------------------------------
    # tenant_role_permissions
    # ---------------------------------------------------------
    # Prevent assigning the same permission to the same
    # tenant role more than once.
    op.create_unique_constraint(
        "uq_role_permission",
        "tenant_role_permissions",
        ["tenant_role_id", "permission_id"],
    )

    # ---------------------------------------------------------
    # tenant_roles
    # ---------------------------------------------------------
    # Prevent duplicate role keys within the same tenant.
    op.create_unique_constraint(
        "uq_tenant_role_key",
        "tenant_roles",
        ["tenant_id", "key"],
    )


def downgrade() -> None:
    # Reverse the constraints/indexes added above.

    op.drop_constraint(
        "uq_tenant_role_key",
        "tenant_roles",
        type_="unique",
    )

    op.drop_constraint(
        "uq_role_permission",
        "tenant_role_permissions",
        type_="unique",
    )

    op.drop_index(
        "ix_membership_user_tenant",
        table_name="memberships",
    )