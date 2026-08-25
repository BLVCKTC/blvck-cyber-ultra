"""upgrade security events model

Revision ID: 3fb7987880ea
Revises: e512b58badb6
Create Date: 2026-08-24 15:03:31.156776

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "3fb7987880ea"
down_revision: Union[str, None] = "e512b58badb6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------
    # 1. Rename existing timestamp column.
    #
    # IMPORTANT:
    # Existing security events already contain timestamp values.
    # Renaming preserves those values and avoids a NOT NULL violation.
    # ---------------------------------------------------------------
    op.alter_column(
        "security_events",
        "timestamp",
        new_column_name="event_time",
    )

    # ---------------------------------------------------------------
    # 2. Add new identity / deduplication fields.
    # ---------------------------------------------------------------
    op.add_column(
        "security_events",
        sa.Column(
            "source_event_id",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "security_events",
        sa.Column(
            "event_fingerprint",
            sa.String(length=128),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------------
    # 3. Add correlation fields.
    # ---------------------------------------------------------------
    op.add_column(
        "security_events",
        sa.Column(
            "correlation_id",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "security_events",
        sa.Column(
            "parent_event_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------------
    # 4. Add ingestion timestamp.
    # Existing rows receive the migration time.
    # ---------------------------------------------------------------
    op.add_column(
        "security_events",
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )

    # Populate existing rows.
    op.execute(
        """
        UPDATE security_events
        SET ingested_at = created_at
        WHERE ingested_at IS NULL
        """
    )

    op.alter_column(
        "security_events",
        "ingested_at",
        nullable=False,
        server_default=sa.text("now()"),
    )

    # ---------------------------------------------------------------
    # 5. Schema / classification fields.
    # ---------------------------------------------------------------
    op.add_column(
        "security_events",
        sa.Column(
            "schema_version",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE security_events
        SET schema_version = 1
        WHERE schema_version IS NULL
        """
    )

    op.alter_column(
        "security_events",
        "schema_version",
        nullable=False,
        server_default=sa.text("1"),
    )

    op.add_column(
        "security_events",
        sa.Column(
            "event_category",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "security_events",
        sa.Column(
            "action",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "security_events",
        sa.Column(
            "risk_score",
            sa.SmallInteger(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------------
    # 6. Network / endpoint fields.
    # ---------------------------------------------------------------
    op.add_column(
        "security_events",
        sa.Column(
            "source_port",
            sa.SmallInteger(),
            nullable=True,
        ),
    )

    op.add_column(
        "security_events",
        sa.Column(
            "destination_port",
            sa.SmallInteger(),
            nullable=True,
        ),
    )

    op.add_column(
        "security_events",
        sa.Column(
            "protocol",
            sa.String(length=32),
            nullable=True,
        ),
    )

    op.add_column(
        "security_events",
        sa.Column(
            "process_name",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "security_events",
        sa.Column(
            "process_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------------
    # 7. MITRE ATT&CK fields.
    # ---------------------------------------------------------------
    op.add_column(
        "security_events",
        sa.Column(
            "mitre_tactic",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "security_events",
        sa.Column(
            "mitre_technique",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "security_events",
        sa.Column(
            "mitre_technique_id",
            sa.String(length=50),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------------
    # 8. Internal event metadata.
    # ---------------------------------------------------------------
    op.add_column(
        "security_events",
        sa.Column(
            "event_metadata",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE security_events
        SET event_metadata = '{}'::jsonb
        WHERE event_metadata IS NULL
        """
    )

    op.alter_column(
        "security_events",
        "event_metadata",
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )

    # ---------------------------------------------------------------
    # 9. Normalize existing JSONB defaults.
    # ---------------------------------------------------------------
    op.alter_column(
        "security_events",
        "raw_event",
        existing_type=postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )

    op.alter_column(
        "security_events",
        "normalized_data",
        existing_type=postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )

    # ---------------------------------------------------------------
    # 10. Convert IP columns from VARCHAR to PostgreSQL INET.
    #
    # Existing values are explicitly cast.
    # ---------------------------------------------------------------
    op.alter_column(
        "security_events",
        "source_ip",
        existing_type=sa.String(length=45),
        type_=postgresql.INET(),
        postgresql_using="source_ip::inet",
        nullable=True,
    )

    op.alter_column(
        "security_events",
        "destination_ip",
        existing_type=sa.String(length=45),
        type_=postgresql.INET(),
        postgresql_using="destination_ip::inet",
        nullable=True,
    )

    # ---------------------------------------------------------------
    # 11. Reduce status column length.
    # Current statuses fit within VARCHAR(20).
    # ---------------------------------------------------------------
    op.alter_column(
        "security_events",
        "status",
        existing_type=sa.String(length=50),
        type_=sa.String(length=20),
        existing_nullable=False,
        server_default=sa.text("'open'"),
    )

    # ---------------------------------------------------------------
    # 12. Add database-level validation.
    # ---------------------------------------------------------------
    op.create_check_constraint(
        "ck_security_events_severity",
        "security_events",
        "severity IN ('info', 'low', 'medium', 'high', 'critical')",
    )

    op.create_check_constraint(
        "ck_security_events_status",
        "security_events",
        "status IN ('open', 'processing', 'processed', 'failed', 'suppressed')",
    )

    op.create_check_constraint(
        "ck_security_events_risk_score",
        "security_events",
        "risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)",
    )

    # ---------------------------------------------------------------
    # 13. Self-referencing parent event relationship.
    # ---------------------------------------------------------------
    op.create_foreign_key(
        "fk_security_events_parent_event_id",
        "security_events",
        "security_events",
        ["parent_event_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ---------------------------------------------------------------
    # 14. Remove old indexes.
    # ---------------------------------------------------------------
    op.drop_index(
        "ix_security_events_tenant_event_type",
        table_name="security_events",
    )

    op.drop_index(
        "ix_security_events_tenant_severity",
        table_name="security_events",
    )

    op.drop_index(
        "ix_security_events_tenant_timestamp",
        table_name="security_events",
    )

    # ---------------------------------------------------------------
    # 15. New indexes.
    # ---------------------------------------------------------------
    op.create_index(
        "ix_security_events_tenant_time",
        "security_events",
        ["tenant_id", "event_time"],
    )

    op.create_index(
        "ix_security_events_tenant_severity_time",
        "security_events",
        ["tenant_id", "severity", "event_time"],
    )

    op.create_index(
        "ix_security_events_correlation_id",
        "security_events",
        ["correlation_id"],
    )

    op.create_index(
        "ix_security_events_event_time",
        "security_events",
        ["event_time"],
    )

    op.create_index(
        "ix_security_events_user_identifier",
        "security_events",
        ["user_identifier"],
    )

    op.create_index(
        "ix_security_events_mitre_technique_id",
        "security_events",
        ["mitre_technique_id"],
    )

    op.create_index(
        "ix_security_events_normalized_data_gin",
        "security_events",
        ["normalized_data"],
        postgresql_using="gin",
    )

    op.create_index(
        "ix_security_events_metadata_gin",
        "security_events",
        ["event_metadata"],
        postgresql_using="gin",
    )

    # ---------------------------------------------------------------
    # 16. Deduplication constraint.
    #
    # source_event_id is nullable, so PostgreSQL allows multiple NULL
    # values. This is intentional for sources without stable IDs.
    # ---------------------------------------------------------------
    op.create_unique_constraint(
        "uq_security_events_tenant_source_event_id",
        "security_events",
        ["tenant_id", "source", "source_event_id"],
    )


def downgrade() -> None:
    # Remove unique constraint.
    op.drop_constraint(
        "uq_security_events_tenant_source_event_id",
        "security_events",
        type_="unique",
    )

    # Remove indexes.
    op.drop_index(
        "ix_security_events_metadata_gin",
        table_name="security_events",
    )

    op.drop_index(
        "ix_security_events_normalized_data_gin",
        table_name="security_events",
    )

    op.drop_index(
        "ix_security_events_mitre_technique_id",
        table_name="security_events",
    )

    op.drop_index(
        "ix_security_events_user_identifier",
        table_name="security_events",
    )

    op.drop_index(
        "ix_security_events_event_time",
        table_name="security_events",
    )

    op.drop_index(
        "ix_security_events_correlation_id",
        table_name="security_events",
    )

    op.drop_index(
        "ix_security_events_tenant_severity_time",
        table_name="security_events",
    )

    op.drop_index(
        "ix_security_events_tenant_time",
        table_name="security_events",
    )

    # Remove foreign key.
    op.drop_constraint(
        "fk_security_events_parent_event_id",
        "security_events",
        type_="foreignkey",
    )

    # Remove checks.
    op.drop_constraint(
        "ck_security_events_risk_score",
        "security_events",
        type_="check",
    )

    op.drop_constraint(
        "ck_security_events_status",
        "security_events",
        type_="check",
    )

    op.drop_constraint(
        "ck_security_events_severity",
        "security_events",
        type_="check",
    )

    # Restore status type.
    op.alter_column(
        "security_events",
        "status",
        existing_type=sa.String(length=20),
        type_=sa.String(length=50),
        existing_nullable=False,
    )

    # Restore IP types.
    op.alter_column(
        "security_events",
        "source_ip",
        existing_type=postgresql.INET(),
        type_=sa.String(length=45),
        postgresql_using="source_ip::text",
        nullable=True,
    )

    op.alter_column(
        "security_events",
        "destination_ip",
        existing_type=postgresql.INET(),
        type_=sa.String(length=45),
        postgresql_using="destination_ip::text",
        nullable=True,
    )

    # Remove event metadata.
    op.drop_column("security_events", "event_metadata")

    # Remove MITRE fields.
    op.drop_column("security_events", "mitre_technique_id")
    op.drop_column("security_events", "mitre_technique")
    op.drop_column("security_events", "mitre_tactic")

    # Remove endpoint fields.
    op.drop_column("security_events", "process_id")
    op.drop_column("security_events", "process_name")
    op.drop_column("security_events", "protocol")
    op.drop_column("security_events", "destination_port")
    op.drop_column("security_events", "source_port")

    # Remove classification fields.
    op.drop_column("security_events", "risk_score")
    op.drop_column("security_events", "action")
    op.drop_column("security_events", "event_category")
    op.drop_column("security_events", "schema_version")

    # Remove ingestion/correlation fields.
    op.drop_column("security_events", "ingested_at")
    op.drop_column("security_events", "parent_event_id")
    op.drop_column("security_events", "correlation_id")
    op.drop_column("security_events", "event_fingerprint")
    op.drop_column("security_events", "source_event_id")

    # Restore timestamp column name.
    op.alter_column(
        "security_events",
        "event_time",
        new_column_name="timestamp",
    )

    # Restore old indexes.
    op.create_index(
        "ix_security_events_tenant_timestamp",
        "security_events",
        ["tenant_id", "timestamp"],
    )

    op.create_index(
        "ix_security_events_tenant_severity",
        "security_events",
        ["tenant_id", "severity"],
    )

    op.create_index(
        "ix_security_events_tenant_event_type",
        "security_events",
        ["tenant_id", "event_type"],
    )