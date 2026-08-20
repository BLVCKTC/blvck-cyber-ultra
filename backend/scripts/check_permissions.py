from collections import Counter

from app.db.seeds.permissions import PERMISSIONS
from app.db.seeds.role_permissions import ROLE_PERMISSIONS


# =========================================================
# PERMISSION DEFINITIONS
# =========================================================

permission_keys = [
    permission[0]
    for permission in PERMISSIONS
]

duplicates = [
    key
    for key, count in Counter(permission_keys).items()
    if count > 1
]

if duplicates:
    print("❌ Duplicate permission definitions:")
    for key in duplicates:
        print(f"   - {key}")
    raise SystemExit(1)

print(
    f"✅ {len(permission_keys)} permission definitions found."
)


# =========================================================
# ROLE PERMISSIONS
# =========================================================

defined_permissions = set(permission_keys)

missing = {}

for role, permissions in ROLE_PERMISSIONS.items():
    unknown = sorted(
        set(permissions) - defined_permissions
    )

    if unknown:
        missing[role] = unknown


if missing:
    print("\n❌ Roles reference undefined permissions:")

    for role, permissions in missing.items():
        print(f"\n{role}:")
        for permission in permissions:
            print(f"   - {permission}")

    raise SystemExit(1)


print("✅ All role permissions reference valid permissions.")


# =========================================================
# DUPLICATES INSIDE ROLES
# =========================================================

for role, permissions in ROLE_PERMISSIONS.items():

    duplicates = [
        key
        for key, count in Counter(permissions).items()
        if count > 1
    ]

    if duplicates:
        print(
            f"\n❌ Duplicate permissions in role {role}:"
        )

        for permission in duplicates:
            print(f"   - {permission}")

        raise SystemExit(1)


print("✅ No duplicate role permissions found.")
print("\n🎉 Permission configuration is consistent.")