import os

from app.core.db import SessionLocal
from app.services.rbac import RBACService


tenant_id = os.environ.get("TEST_TENANT_ID")
if not tenant_id:
    raise RuntimeError("Set TEST_TENANT_ID to run the RBAC smoke test")

db = SessionLocal()
try:
    rbac = RBACService(db)
    result = rbac.get_authorization_context(
        user_id=os.environ.get("TEST_USER_ID", ""),
        tenant_id=tenant_id,
    )
    print(result)
finally:
    db.close()
