from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.enums import MembershipRole
from app.db.models.permission import Permission
from app.db.models.role_permission import RolePermission
from app.db.models.tenant_role import TenantRole
from app.db.models.tenant_role_permission import TenantRolePermission
from app.db.seeds.tenant_roles import TENANT_ROLES


def ensure_tenant_role(db: Session, *, tenant_id, role: MembershipRole) -> TenantRole:
    """Get-or-create the TenantRole (and its TenantRolePermission rows)
    for one (tenant, role) pair, on demand.

    This is the single code path that should ever produce a
    Membership.tenant_role_id going forward — it exists because nothing
    in the application previously created TenantRole rows outside the
    standalone seed script, which only backfills existing tenants and
    never runs automatically for new ones or new members.

    Definitions come from the same canonical TENANT_ROLES /
    ROLE_PERMISSIONS tables the seed script uses, so a tenant provisioned
    through the app and one backfilled by the seed script end up
    identical — this is not a second, diverging definition of roles.
    """
    role_key = role.value if hasattr(role, "value") else str(role)

    tenant_role = (
        db.query(TenantRole)
        .filter(TenantRole.tenant_id == tenant_id, TenantRole.key == role_key)
        .first()
    )

    if tenant_role is None:
        definition = next((r for r in TENANT_ROLES if r["key"] == role_key), None)
        if definition is None:
            raise ValueError(f"No TENANT_ROLES definition found for role '{role_key}'")

        tenant_role = TenantRole(
            tenant_id=tenant_id,
            key=definition["key"],
            name=definition["name"],
            description=definition["description"],
            is_system=definition["is_system"],
            is_default=definition["is_default"],
        )
        db.add(tenant_role)
        db.flush()  # need tenant_role.id before creating permission links

        _ensure_tenant_role_permissions(db, tenant_role)

    return tenant_role


def _ensure_tenant_role_permissions(db: Session, tenant_role: TenantRole) -> None:
    """Copy this role's permission set from the global RolePermission
    template table into TenantRolePermission rows for this specific
    tenant's role instance."""
    permission_ids = (
        db.query(RolePermission.permission_id)
        .filter(RolePermission.role_key == tenant_role.key)
        .all()
    )

    for (permission_id,) in permission_ids:
        db.add(
            TenantRolePermission(
                tenant_role_id=tenant_role.id,
                permission_id=permission_id,
            )
        )