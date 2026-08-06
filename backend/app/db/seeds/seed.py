from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.permission import Permission
from app.db.models.role_permission import RolePermission
from app.db.models.tenant_role import TenantRole
from app.db.models.tenant_role_permission import TenantRolePermission
from app.db.models.tenant import Tenant

from app.db.seeds.permissions import PERMISSIONS
from app.db.seeds.role_permissions import ROLE_PERMISSIONS
from app.db.seeds.tenant_roles import TENANT_ROLES


class SeedRunner:
    """
    Database seed runner.

    Safe to run multiple times.

    Seeds:
    - permissions
    - global role permissions
    - tenant roles
    - tenant role permissions

    Existing records are updated.
    Missing records are inserted.
    """

    def __init__(self, db: Session):
        self.db = db


    # =========================================================
    # Permissions
    # =========================================================

    def seed_permissions(self) -> None:

        print("Seeding permissions...")

        created = 0
        updated = 0


        for (
            key,
            name,
            category,
            description,
            risk_level,
        ) in PERMISSIONS:


            permission = (
                self.db.query(Permission)
                .filter(
                    Permission.key == key
                )
                .first()
            )


            if permission is None:

                permission = Permission(
                    key=key,
                    name=name,
                    category=category,
                    description=description,
                    risk_level=risk_level,
                )

                self.db.add(permission)

                created += 1


            else:

                permission.name = name
                permission.category = category
                permission.description = description
                permission.risk_level = risk_level

                updated += 1


        self.db.commit()


        print(
            f"Created permissions: {created}"
        )

        print(
            f"Updated permissions: {updated}"
        )



    # =========================================================
    # Global Role -> Permission
    # =========================================================

    def seed_role_permissions(self) -> None:

        print(
            "Seeding role permissions..."
        )


        permission_lookup = {
            permission.key: permission.id
            for permission in self.db.query(Permission).all()
        }


        created = 0
        existing_count = 0
        missing = []


        for role_key, permission_keys in ROLE_PERMISSIONS.items():


            for permission_key in permission_keys:


                permission_id = permission_lookup.get(
                    permission_key
                )


                if permission_id is None:

                    missing.append(
                        permission_key
                    )

                    continue



                existing = (
                    self.db.query(RolePermission)
                    .filter(
                        RolePermission.role_key == role_key,
                        RolePermission.permission_id == permission_id,
                    )
                    .first()
                )


                if existing:

                    existing_count += 1

                    continue



                self.db.add(
                    RolePermission(
                        role_key=role_key,
                        permission_id=permission_id,
                    )
                )

                created += 1



        self.db.commit()


        print(
            f"Created role permissions: {created}"
        )

        print(
            f"Existing role permissions: {existing_count}"
        )


        if missing:

            print()
            print("------------------------------")
            print("Missing permissions")
            print("------------------------------")

            for permission in sorted(set(missing)):
                print(
                    f"- {permission}"
                )

            print("------------------------------")



    # =========================================================
    # Tenant Roles
    # =========================================================

    def seed_tenant_roles(self) -> None:

        print(
            "Seeding tenant roles..."
        )


        tenants = (
            self.db.query(Tenant)
            .all()
        )


        if not tenants:

            print(
                "No tenants found. Skipping tenant roles."
            )

            return



        created = 0
        updated = 0



        for tenant in tenants:


            for role in TENANT_ROLES:


                existing = (
                    self.db.query(TenantRole)
                    .filter(
                        TenantRole.tenant_id == tenant.id,
                        TenantRole.key == role["key"],
                    )
                    .first()
                )



                if existing is None:


                    self.db.add(
                        TenantRole(
                            tenant_id=tenant.id,
                            key=role["key"],
                            name=role["name"],
                            description=role["description"],
                            is_system=role["is_system"],
                            is_default=role["is_default"],
                        )
                    )

                    created += 1



                else:


                    existing.name = role["name"]
                    existing.description = role["description"]
                    existing.is_system = role["is_system"]
                    existing.is_default = role["is_default"]


                    updated += 1



        self.db.commit()



        print(
            f"Created tenant roles: {created}"
        )

        print(
            f"Updated tenant roles: {updated}"
        )



    # =========================================================
    # Tenant Role -> Permission
    # =========================================================

    def seed_tenant_role_permissions(self) -> None:

        print(
            "Seeding tenant role permissions..."
        )


        global_permissions = (
            self.db.query(RolePermission)
            .all()
        )


        role_permission_map: dict[str, list[int]] = {}



        for item in global_permissions:

            role_permission_map.setdefault(
                item.role_key,
                []
            ).append(
                item.permission_id
            )



        tenant_roles = (
            self.db.query(TenantRole)
            .all()
        )


        created = 0
        existing_count = 0



        for tenant_role in tenant_roles:


            permission_ids = (
                role_permission_map.get(
                    tenant_role.key,
                    []
                )
            )



            for permission_id in permission_ids:


                existing = (
                    self.db.query(TenantRolePermission)
                    .filter(
                        TenantRolePermission.tenant_role_id
                        == tenant_role.id,

                        TenantRolePermission.permission_id
                        == permission_id,
                    )
                    .first()
                )


                if existing:

                    existing_count += 1

                    continue



                self.db.add(
                    TenantRolePermission(
                        tenant_role_id=tenant_role.id,
                        permission_id=permission_id,
                    )
                )

                created += 1



        self.db.commit()



        print(
            f"Created tenant role permissions: {created}"
        )

        print(
            f"Existing tenant role permissions: {existing_count}"
        )



    # =========================================================
    # Runner
    # =========================================================

    def run(self) -> None:


        print("----------------------------------------")
        print("Running database seed...")
        print("----------------------------------------")


        self.seed_permissions()

        self.seed_role_permissions()

        self.seed_tenant_roles()

        self.seed_tenant_role_permissions()


        print("----------------------------------------")
        print("Database seed complete.")
        print("----------------------------------------")