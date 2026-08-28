"""merge foundation and operations migration heads

Revision ID: 1540f7fc462a
Revises: f3a7d1c8b204, f4a7b8c9d012
Create Date: 2026-08-28 10:46:02.074036

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa




# revision identifiers, used by Alembic.
revision: str = '1540f7fc462a'
down_revision: Union[str, None] = ('f3a7d1c8b204', 'f4a7b8c9d012')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass