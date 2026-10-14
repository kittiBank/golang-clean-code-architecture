"""Repository interfaces. Use cases depend on these, not on SQLAlchemy."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from app.core.database import Base
from app.models import User, UserPermission, UserToken


class UserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def create(
        self, *, email: str, password_hash: str, first_name: str, last_name: str
    ) -> User:
        """Raises AlreadyExistsError if the email is taken."""

    @abstractmethod
    def get_token_by_user_id(self, user_id: int) -> UserToken | None: ...

    @abstractmethod
    def get_token_by_access(self, user_id: int, access: str) -> UserToken | None: ...

    @abstractmethod
    def upsert_token(self, user_id: int, access: str, refresh: str) -> None:
        """Store the user's session, replacing any previous one (one session per user)."""

    @abstractmethod
    def delete_token(self, user_id: int) -> None: ...

    @abstractmethod
    def get_permission(self, user_id: int) -> UserPermission | None: ...


class CrudRepository(ABC):
    """Generic read access to any registered model."""

    @abstractmethod
    def get_by_id(self, model: type[Base], record_id: int) -> Base | None: ...

    @abstractmethod
    def list(
        self, model: type[Base], *, offset: int, limit: int, filters: dict[str, Any]
    ) -> tuple[Sequence[Base], int]:
        """Return one page of records (ordered by id) and the total count matching `filters`."""
