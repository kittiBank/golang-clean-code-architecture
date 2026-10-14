from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.domain.exceptions import AlreadyExistsError
from app.domain.repositories import UserRepository
from app.models import User, UserPermission, UserToken


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def create(
        self, *, email: str, password_hash: str, first_name: str, last_name: str
    ) -> User:
        user = User(
            email=email, password=password_hash, first_name=first_name, last_name=last_name
        )
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise AlreadyExistsError("email has already been used")
        return user

    def get_token_by_user_id(self, user_id: int) -> UserToken | None:
        return self.db.scalar(
            select(UserToken).options(joinedload(UserToken.user)).where(UserToken.user_id == user_id)
        )

    def get_token_by_access(self, user_id: int, access: str) -> UserToken | None:
        return self.db.scalar(
            select(UserToken)
            .options(joinedload(UserToken.user))
            .where(UserToken.user_id == user_id, UserToken.access == access)
        )

    def upsert_token(self, user_id: int, access: str, refresh: str) -> None:
        token = self.db.scalar(select(UserToken).where(UserToken.user_id == user_id))
        if token is None:
            token = UserToken(user_id=user_id)
            self.db.add(token)
        token.access = access
        token.refresh = refresh
        self.db.commit()

    def delete_token(self, user_id: int) -> None:
        self.db.execute(delete(UserToken).where(UserToken.user_id == user_id))
        self.db.commit()

    def get_permission(self, user_id: int) -> UserPermission | None:
        return self.db.scalar(select(UserPermission).where(UserPermission.user_id == user_id))
