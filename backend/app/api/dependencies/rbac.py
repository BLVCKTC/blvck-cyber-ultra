from sqlalchemy.orm import Session

from app.services.rbac import RBACService



def get_rbac_service(
    db: Session,
) -> RBACService:

    return RBACService(db)