"""In-memory repositories, so use cases can be tested without a database."""

from collections.abc import Sequence
from typing import Any

from app.core.database import Base
from app.domain.exceptions import AlreadyExistsError
from app.domain.repositories import CrudRepository, UserRepository
from app.models import User, UserPermission, UserToken


class FakeUserRepository(UserRepository):
    def __init__(self):
        self.users: dict[int, User] = {}
        self.tokens: dict[int, UserToken] = {}  # by user_id
        self.permissions: dict[int, UserPermission] = {}  # by user_id

    def get_by_email(self, email: str) -> User | None:
        return next((user for user in self.users.values() if user.email == email), None)

    def create(
        self, *, email: str, password_hash: str, first_name: str, last_name: str
    ) -> User:
        if self.get_by_email(email) is not None:
            raise AlreadyExistsError("email has already been used")
        user = User(
            id=len(self.users) + 1,
            email=email,
            password=password_hash,
            first_name=first_name,
            last_name=last_name,
        )
        self.users[user.id] = user
        return user

    def get_token_by_user_id(self, user_id: int) -> UserToken | None:
        return self.tokens.get(user_id)

    def get_token_by_access(self, user_id: int, access: str) -> UserToken | None:
        token = self.tokens.get(user_id)
        return token if token is not None and token.access == access else None

    def upsert_token(self, user_id: int, access: str, refresh: str) -> None:
        self.tokens[user_id] = UserToken(
            user_id=user_id, access=access, refresh=refresh, user=self.users.get(user_id)
        )

    def delete_token(self, user_id: int) -> None:
        self.tokens.pop(user_id, None)

    def get_permission(self, user_id: int) -> UserPermission | None:
        return self.permissions.get(user_id)


class FakeCrudRepository(CrudRepository):
    def __init__(self, records: list[Base]):
        self.records = records
        self.last_list_call: dict[str, Any] | None = None

    def get_by_id(self, model: type[Base], record_id: int) -> Base | None:
        return next(
            (r for r in self.records if isinstance(r, model) and r.id == record_id), None
        )

    def list(
        self, model: type[Base], *, offset: int, limit: int, filters: dict[str, Any]
    ) -> tuple[Sequence[Base], int]:
        self.last_list_call = {"offset": offset, "limit": limit, "filters": filters}
        matches = [
            r
            for r in self.records
            if isinstance(r, model) and all(getattr(r, f) == v for f, v in filters.items())
        ]
        return matches[offset : offset + limit], len(matches)
