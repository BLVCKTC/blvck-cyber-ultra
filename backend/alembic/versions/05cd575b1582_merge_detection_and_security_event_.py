"""merge detection and security event migration heads

Revision ID: 05cd575b1582
Revises: c8f3a5b19d27, f0a04bc38671
Create Date: 2026-08-26 13:22:13.739739

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa




# revision identifiers, used by Alembic.
revision: str = '05cd575b1582'
down_revision: Union[str, None] = ('c8f3a5b19d27', 'f0a04bc38671')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass