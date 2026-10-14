"""Repository interfaces. Use cases depend on these, not on SQLAlchemy."""

from abc import ABC, abstractmethod

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
