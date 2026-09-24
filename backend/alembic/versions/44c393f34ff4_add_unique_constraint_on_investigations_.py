"""add unique constraint on investigations tenant_id, alert_id

Revision ID: 44c393f34ff4
Revises: 7a91d4c8e2f3
Create Date: 2026-09-24 08:38:50.105559

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa




# revision identifiers, used by Alembic.
revision: str = '44c393f34ff4'
down_revision: Union[str, None] = '7a91d4c8e2f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NULL != NULL in Postgres uniqueness checks, so this only enforces
    # uniqueness among non-null alert_id values — manual investigations
    # with no alert_id are unaffected. If any tenant already has
    # duplicate (tenant_id, alert_id) rows from the race this is fixing,
    # this ADD CONSTRAINT will fail loudly rather than silently allow
    # the data problem forward. Check first if unsure:
    #   SELECT tenant_id, alert_id, COUNT(*) FROM investigations
    #   WHERE alert_id IS NOT NULL
    #   GROUP BY tenant_id, alert_id HAVING COUNT(*) > 1;
    op.execute(
        "ALTER TABLE investigations ADD CONSTRAINT "
        "uq_investigations_tenant_alert UNIQUE (tenant_id, alert_id)"
    )
 
 
def downgrade() -> None:
    op.execute(
        "ALTER TABLE investigations DROP CONSTRAINT uq_investigations_tenant_alert"
    )