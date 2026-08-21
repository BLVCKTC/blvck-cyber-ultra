from __future__ import annotations

from sqlalchemy import select

from app.core.db import SessionLocal
from app.db.models.enums import MembershipRole
from app.db.models.membership import Membership
from app.db.models.tenant import Tenant
from app.db.models.tenant_role import TenantRole
from app.db.models.user import User


# ============================================================
# KEYCLOAK USER → LOCAL TENANT MAPPING
# ============================================================

MINING_USERS = [
    {
        "username": "greatdyke.admin",
        "email": "admin@greatdykemining.com",
        "keycloak_sub": "bd126179-7401-4614-bf0b-91ca0398eb4b",
        "tenant_slug": "great-dyke-mining",
        "role": "ADMIN",
    },
    {
        "username": "greatdyke.socmanager",
        "email": "socmanager@greatdykemining.com",
        "keycloak_sub": "e32c145d-39d8-48dc-8666-5f5b50de775a",
        "tenant_slug": "great-dyke-mining",
        "role": "SOC_MANAGER",
    },
    {
        "username": "greatdyke.analyst",
        "email": "analyst@greatdykemining.com",
        "keycloak_sub": "63a7551b-f191-4efd-ad6a-06862e67050c",
        "tenant_slug": "great-dyke-mining",
        "role": "SOC_ANALYST",
    },

    {
        "username": "hwange.admin",
        "email": "admin@hwangeminerals.com",
        "keycloak_sub": "3e65f33a-6d1a-4fe7-b447-f59a3d24c0ca",
        "tenant_slug": "hwange-minerals",
        "role": "ADMIN",
    },
    {
        "username": "hwange.socmanager",
        "email": "socmanager@hwangeminerals.com",
        "keycloak_sub": "74ed731b-188f-4f28-8919-15951aee5fc3",
        "tenant_slug": "hwange-minerals",
        "role": "SOC_MANAGER",
    },
    {
        "username": "hwange.analyst",
        "email": "analyst@hwangeminerals.com",
        "keycloak_sub": "63f7c285-88e6-4df3-8de9-1175a75ce14f",
        "tenant_slug": "hwange-minerals",
        "role": "SOC_ANALYST",
    },

    {
        "username": "midlands.admin",
        "email": "admin@midlandschrome.com",
        "keycloak_sub": "2b64e557-fb4d-47ba-add7-a8df80ac09e4",
        "tenant_slug": "midlands-chrome",
        "role": "ADMIN",
    },
    {
        "username": "midlands.socmanager",
        "email": "socmanager@midlandschrome.com",
        "keycloak_sub": "d69c7c32-c8de-4523-8ea5-878d3ff5d276",
        "tenant_slug": "midlands-chrome",
        "role": "SOC_MANAGER",
    },
    {
        "username": "midlands.analyst",
        "email": "analyst@midlandschrome.com",
        "keycloak_sub": "a757c79a-46b9-41c2-838f-09885d29c039",
        "tenant_slug": "midlands-chrome",
        "role": "SOC_ANALYST",
    },

    {
        "username": "matabeleland.admin",
        "email": "admin@matabelelandgold.com",
        "keycloak_sub": "3e18208e-9f9c-42cf-96f7-7f9dc235e600",
        "tenant_slug": "matabeleland-gold",
        "role": "ADMIN",
    },
    {
        "username": "matabeleland.socmanager",
        "email": "socmanager@matabelelandgold.com",
        "keycloak_sub": "ec40d113-0b04-4195-a489-c313567c7b8e",
        "tenant_slug": "matabeleland-gold",
        "role": "SOC_MANAGER",
    },
    {
        "username": "matabeleland.analyst",
        "email": "analyst@matabelelandgold.com",
        "keycloak_sub": "a1ab2080-3f4e-4afb-a179-a81fb73faf2c",
        "tenant_slug": "matabeleland-gold",
        "role": "SOC_ANALYST",
    },
]


# ============================================================
# HELPERS
# ============================================================

def get_or_create_user(db, user_data: dict) -> User:
    user = db.scalar(
        select(User).where(
            User.keycloak_sub == user_data["keycloak_sub"]
        )
    )

    if user is None:
        user = User(
            keycloak_sub=user_data["keycloak_sub"],
            email=user_data["email"],
            name=user_data["username"],
        )

        db.add(user)
        db.flush()

        print(
            f"  CREATED USER: "
            f"{user_data['username']} "
            f"({user.id})"
        )

    else:
        changed = False

        if user.email != user_data["email"]:
            user.email = user_data["email"]
            changed = True

        if user.name != user_data["username"]:
            user.name = user_data["username"]
            changed = True

        if changed:
            db.flush()

        print(
            f"  EXISTING USER: "
            f"{user_data['username']} "
            f"({user.id})"
        )

    return user


def get_tenant(db, slug: str) -> Tenant:
    tenant = db.scalar(
        select(Tenant).where(
            Tenant.slug == slug
        )
    )

    if tenant is None:
        raise RuntimeError(
            f"Tenant not found: {slug}"
        )

    return tenant


def get_tenant_role(
    db,
    tenant_id,
    role_key: str,
) -> TenantRole:
    tenant_role = db.scalar(
        select(TenantRole).where(
            TenantRole.tenant_id == tenant_id,
            TenantRole.key == role_key,
        )
    )

    if tenant_role is None:
        raise RuntimeError(
            f"Tenant role not found: "
            f"tenant={tenant_id}, role={role_key}"
        )

    return tenant_role


# ============================================================
# MEMBERSHIP SYNCHRONIZATION
# ============================================================

def sync_membership(
    db,
    user: User,
    tenant: Tenant,
    tenant_role: TenantRole,
    role_key: str,
) -> Membership:

    membership = db.scalar(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.tenant_id == tenant.id,
        )
    )

    membership_role = MembershipRole(role_key)

    if membership is None:

        membership = Membership(
            user_id=user.id,
            tenant_id=tenant.id,
            tenant_role_id=tenant_role.id,
            role=membership_role,
            is_default=False,
        )

        db.add(membership)
        db.flush()

        print(
            f"  CREATED MEMBERSHIP: "
            f"{user.name} → {tenant.slug} → {role_key}"
        )

    else:

        changed = False

        if membership.role != membership_role:
            membership.role = membership_role
            changed = True

        if membership.tenant_role_id != tenant_role.id:
            membership.tenant_role_id = tenant_role.id
            changed = True

        if changed:
            db.flush()

            print(
                f"  UPDATED MEMBERSHIP: "
                f"{user.name} → {tenant.slug} → {role_key}"
            )
        else:
            print(
                f"  EXISTING MEMBERSHIP: "
                f"{user.name} → {tenant.slug} → {role_key}"
            )

    return membership


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 60)
    print("BLVCK CYBER — Mining Keycloak Synchronization")
    print("=" * 60)

    db = SessionLocal()

    try:

        created_users = 0
        existing_users = 0
        created_memberships = 0
        existing_memberships = 0

        for data in MINING_USERS:

            print()
            print(
                f"Processing: "
                f"{data['username']}"
            )

            tenant = get_tenant(
                db,
                data["tenant_slug"],
            )

            tenant_role = get_tenant_role(
                db,
                tenant.id,
                data["role"],
            )

            existing_user = db.scalar(
                select(User).where(
                    User.keycloak_sub == data["keycloak_sub"]
                )
            )

            user = get_or_create_user(
                db,
                data,
            )

            if existing_user is None:
                created_users += 1
            else:
                existing_users += 1

            existing_membership = db.scalar(
                select(Membership).where(
                    Membership.user_id == user.id,
                    Membership.tenant_id == tenant.id,
                )
            )

            membership = sync_membership(
                db=db,
                user=user,
                tenant=tenant,
                tenant_role=tenant_role,
                role_key=data["role"],
            )

            if existing_membership is None:
                created_memberships += 1
            else:
                existing_memberships += 1

        # ----------------------------------------------------
        # Set the first mining membership for each user as
        # their default tenant.
        #
        # Since each seeded mining user belongs to exactly
        # one mining tenant, this is deterministic.
        # ----------------------------------------------------

        for data in MINING_USERS:

            user = db.scalar(
                select(User).where(
                    User.keycloak_sub == data["keycloak_sub"]
                )
            )

            tenant = get_tenant(
                db,
                data["tenant_slug"],
            )

            membership = db.scalar(
                select(Membership).where(
                    Membership.user_id == user.id,
                    Membership.tenant_id == tenant.id,
                )
            )

            if membership is None:
                raise RuntimeError(
                    f"Membership disappeared for "
                    f"{data['username']}"
                )

            membership.is_default = True

        db.commit()

        print()
        print("=" * 60)
        print("SYNCHRONIZATION COMPLETE")
        print("=" * 60)
        print(f"Users created:              {created_users}")
        print(f"Users existing:             {existing_users}")
        print(f"Memberships created:        {created_memberships}")
        print(f"Memberships existing:       {existing_memberships}")
        print("=" * 60)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
