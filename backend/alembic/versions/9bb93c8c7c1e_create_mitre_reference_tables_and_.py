"""create mitre reference tables and detection_rule_technique join tables

Revision ID: 9bb93c8c7c1e
Revises: 9f5d3ec2043c
Create Date: 2026-09-11 08:47:17.351897

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = '9bb93c8c7c1e'
down_revision: Union[str, None] = '9f5d3ec2043c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


MITRE_DOMAIN_VALUES = ("enterprise-attack", "ics-attack", "mobile-attack")
MITRE_SYNC_STATUS_VALUES = ("running", "success", "failed")


def upgrade() -> None:
    bind = op.get_bind()

    mitre_domain = postgresql.ENUM(*MITRE_DOMAIN_VALUES, name="mitre_domain")
    mitre_domain.create(bind, checkfirst=True)
    mitre_sync_status = postgresql.ENUM(*MITRE_SYNC_STATUS_VALUES, name="mitre_sync_status")
    mitre_sync_status.create(bind, checkfirst=True)

    domain_col = lambda: postgresql.ENUM(*MITRE_DOMAIN_VALUES, name="mitre_domain", create_type=False)

    op.create_table(
        "mitre_tactic",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False, index=True),
        sa.Column("shortname", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("domain", domain_col(), nullable=False),
        sa.Column("url", sa.String(512)),
        sa.Column("stix_id", sa.String(128), nullable=False, unique=True),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_tactic_id_domain"),
    )

    op.create_table(
        "mitre_technique",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("domain", domain_col(), nullable=False),
        sa.Column("is_subtechnique", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("parent_technique_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_technique.id", ondelete="SET NULL")),
        sa.Column("platforms", postgresql.ARRAY(sa.String())),
        sa.Column("data_sources", postgresql.ARRAY(sa.String())),
        sa.Column("detection_guidance", sa.Text()),
        sa.Column("url", sa.String(512)),
        sa.Column("stix_id", sa.String(128), nullable=False, unique=True),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_technique_id_domain"),
    )

    op.create_table(
        "mitre_mitigation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("domain", domain_col(), nullable=False),
        sa.Column("url", sa.String(512)),
        sa.Column("stix_id", sa.String(128), nullable=False, unique=True),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_mitigation_id_domain"),
    )

    op.create_table(
        "mitre_group",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("aliases", postgresql.ARRAY(sa.String())),
        sa.Column("description", sa.Text()),
        sa.Column("domain", domain_col(), nullable=False),
        sa.Column("url", sa.String(512)),
        sa.Column("stix_id", sa.String(128), nullable=False, unique=True),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_group_id_domain"),
    )

    op.create_table(
        "mitre_software",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("aliases", postgresql.ARRAY(sa.String())),
        sa.Column("software_type", sa.String(32), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("domain", domain_col(), nullable=False),
        sa.Column("url", sa.String(512)),
        sa.Column("stix_id", sa.String(128), nullable=False, unique=True),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_software_id_domain"),
    )

    op.create_table(
        "mitre_campaign",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("first_seen", sa.DateTime(timezone=True)),
        sa.Column("last_seen", sa.DateTime(timezone=True)),
        sa.Column("domain", domain_col(), nullable=False),
        sa.Column("url", sa.String(512)),
        sa.Column("stix_id", sa.String(128), nullable=False, unique=True),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_campaign_id_domain"),
    )

    op.create_table(
        "mitre_technique_tactic",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_technique_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_technique.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mitre_tactic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_tactic.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("mitre_technique_id", "mitre_tactic_id", name="uq_technique_tactic"),
    )

    op.create_table(
        "mitre_technique_mitigation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_technique_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_technique.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mitre_mitigation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_mitigation.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.Text()),
        sa.UniqueConstraint("mitre_technique_id", "mitre_mitigation_id", name="uq_technique_mitigation"),
    )

    op.create_table(
        "mitre_group_technique",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_group.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mitre_technique_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_technique.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.Text()),
        sa.UniqueConstraint("mitre_group_id", "mitre_technique_id", name="uq_group_technique"),
    )

    op.create_table(
        "mitre_software_technique",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_software_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_software.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mitre_technique_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_technique.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.Text()),
        sa.UniqueConstraint("mitre_software_id", "mitre_technique_id", name="uq_software_technique"),
    )

    op.create_table(
        "mitre_campaign_technique",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_campaign.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mitre_technique_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_technique.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("mitre_campaign_id", "mitre_technique_id", name="uq_campaign_technique"),
    )

    op.create_table(
        "mitre_campaign_group",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_campaign.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mitre_group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_group.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("mitre_campaign_id", "mitre_group_id", name="uq_campaign_group"),
    )

    op.create_table(
        "mitre_sync_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("domain", domain_col(), nullable=False),
        sa.Column("mitre_version", sa.String(32)),
        sa.Column("source_url", sa.String(512), nullable=False),
        sa.Column("status", postgresql.ENUM(*MITRE_SYNC_STATUS_VALUES, name="mitre_sync_status", create_type=False), nullable=False, server_default="running"),
        sa.Column("objects_created", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("objects_updated", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("objects_deprecated", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )

    # Tenant-scoped bridge — FKs corrected to detection_rules (plural)
    # and created_by now a real FK, per the two fixes flagged above.
    op.create_table(
        "detection_rule_technique",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("detection_rule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("detection_rules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mitre_technique_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mitre_technique.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.UniqueConstraint("detection_rule_id", "mitre_technique_id", name="uq_rule_technique"),
    )
    op.create_index("ix_detection_rule_technique_rule", "detection_rule_technique", ["detection_rule_id"])
    op.create_index("ix_detection_rule_technique_technique", "detection_rule_technique", ["mitre_technique_id"])

    op.execute("ALTER TABLE detection_rule_technique ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE detection_rule_technique FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation_detection_rule_technique ON detection_rule_technique
        USING (
            EXISTS (
                SELECT 1 FROM detection_rules dr
                WHERE dr.id = detection_rule_technique.detection_rule_id
                AND dr.tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM detection_rules dr
                WHERE dr.id = detection_rule_technique.detection_rule_id
                AND dr.tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
            )
        )
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_detection_rule_technique ON detection_rule_technique")
    op.drop_table("detection_rule_technique")
    op.drop_table("mitre_sync_log")
    op.drop_table("mitre_campaign_group")
    op.drop_table("mitre_campaign_technique")
    op.drop_table("mitre_software_technique")
    op.drop_table("mitre_group_technique")
    op.drop_table("mitre_technique_mitigation")
    op.drop_table("mitre_technique_tactic")
    op.drop_table("mitre_campaign")
    op.drop_table("mitre_software")
    op.drop_table("mitre_group")
    op.drop_table("mitre_mitigation")
    op.drop_table("mitre_technique")
    op.drop_table("mitre_tactic")

    bind = op.get_bind()
    postgresql.ENUM(name="mitre_sync_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="mitre_domain").drop(bind, checkfirst=True)