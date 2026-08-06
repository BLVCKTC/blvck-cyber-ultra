from app.core.db import SessionLocal
from app.services.rbac import RBACService



db = SessionLocal()


rbac = RBACService(db)


result = rbac.get_authorization_context(

    user_id=2,

    tenant_id="BLVCK-CYBER"

)


print(result)


db.close()