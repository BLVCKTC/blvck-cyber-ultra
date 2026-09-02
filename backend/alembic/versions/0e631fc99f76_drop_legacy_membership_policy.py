"""drop legacy membership policy

Revision ID: 0e631fc99f76
Revises: 7937e89cd9f4
Create Date: 2026-08-31 09:51:17.272245

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa




# revision identifiers, used by Alembic.
revision: str = '0e631fc99f76'
down_revision: Union[str, None] = '7937e89cd9f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP POLICY IF EXISTS user_scoped_memberships ON memberships")


def downgrade() -> None:
    # Not recreated — this was the earlier, narrower policy superseded by
    # membership_visibility in 7937e89cd9f4. Discarded intentionally, not
    # an oversight.
    pass