from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.services.rbac import RBACService
from app.core.keycloak import get_current_user



# -----------------------------------------
# Database dependency
# -----------------------------------------

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



# -----------------------------------------
# Permission dependency
# -----------------------------------------

def require_permission(permission_key: str):

    """
    Database-backed RBAC permission guard.

    Example:

    Depends(
        require_permission("alerts.view")
    )

    """


    def permission_checker(

        current_user = Depends(get_current_user),

        db: Session = Depends(get_db),

    ):


        if not current_user:

            raise HTTPException(

                status_code=status.HTTP_401_UNAUTHORIZED,

                detail="Authentication required",

            )


        user_id = current_user["id"]

        tenant_id = current_user["tenant_id"]



        rbac = RBACService(db)


        allowed = rbac.has_permission(

            user_id=user_id,

            tenant_id=tenant_id,

            permission_key=permission_key,

        )



        if not allowed:

            raise HTTPException(

                status_code=status.HTTP_403_FORBIDDEN,

                detail={

                    "error": "permission_denied",

                    "required_permission": permission_key,

                },

            )


        return True


    return permission_checker