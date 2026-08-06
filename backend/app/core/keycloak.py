from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.db.models.user import User
from app.db.models.membership import Membership


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/auth/login",
    tokenUrl="/auth/token",
)


KEYCLOAK_PUBLIC_KEY = """
YOUR_KEYCLOAK_PUBLIC_KEY
"""


ALGORITHM = "RS256"



def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    try:

        payload = jwt.decode(
            token,
            KEYCLOAK_PUBLIC_KEY,
            algorithms=[ALGORITHM],
            options={
                "verify_aud": False
            },
        )


        keycloak_id = payload.get("sub")


        if not keycloak_id:

            raise Exception(
                "Missing Keycloak subject"
            )



        user = (
            db.query(User)
            .filter(
                User.keycloak_id == keycloak_id
            )
            .first()
        )


        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not registered",
            )



        membership = (
            db.query(Membership)
            .filter(
                Membership.user_id == user.id
            )
            .first()
        )


        if not membership:

            raise HTTPException(
                status_code=403,
                detail="User has no tenant access",
            )



        return {

            "id": user.id,

            "keycloak_id": user.keycloak_id,

            "email": user.email,

            "name": user.name,

            "tenant_id": membership.tenant_id,

        }



    except HTTPException:

        raise



    except Exception as e:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Invalid authentication token",

        )