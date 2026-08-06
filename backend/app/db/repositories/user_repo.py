from sqlalchemy.orm import Session

from app.db.models.user import User

class UserRepo:

    def __init__(self, db: Session):
        self.db = db

    def get(
        self,
        user_id: int,
    ) -> User | None:

        return self.db.get(
            User,
            user_id,
        )


    def get_by_keycloak_sub(
        self,
        keycloak_sub: str,
    ) -> User | None:

        return (
            self.db.query(User)
            .filter(
                User.keycloak_sub == keycloak_sub
            )
            .first()
        )


    def create(
        self,
        *,
        keycloak_sub: str,
        email: str | None,
        name: str | None,
    ) -> User:

        user = User(
            keycloak_sub=keycloak_sub,
            email=email,
            name=name,
        )

        self.db.add(user)

        self.db.flush()

        self.db.refresh(user)

        return user

    def update(
        self,
        user: User,
        *,
        email: str | None,
        name: str | None,
    ) -> User:

        changed = False


        if email and user.email != email:
            user.email = email
            changed = True


        if name and user.name != name:
            user.name = name
            changed = True


        if changed:
            self.db.flush()
            self.db.refresh(user)

        return user

    def upsert_from_token(
        self,
        *,
        keycloak_sub: str,
        email: str | None,
        name: str | None,
    ) -> User:
        user = self.get_by_keycloak_sub(
            keycloak_sub
        )
        if user is None:

            user = self.create(
                keycloak_sub=keycloak_sub,
                email=email,
                name=name,
            )

            return user
        return self.update(
            user,
            email=email,
            name=name,
        )