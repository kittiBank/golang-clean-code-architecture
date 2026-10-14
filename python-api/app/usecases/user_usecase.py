from dataclasses import dataclass

from app.core.security import (
    TokenClaims,
    TokenType,
    create_token,
    hash_password,
    parse_token,
    verify_password,
)
from app.domain.exceptions import AlreadyExistsError, AuthenticationError
from app.domain.repositories import UserRepository
from app.domain.schemas.user import (
    TokenPair,
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserResponse,
)
from app.models import User, UserPermission, UserToken


@dataclass(frozen=True)
class AuthContext:
    """Who is calling: set on every authenticated request."""

    user: User
    permission: UserPermission | None


class UserUsecase:
    def __init__(self, users: UserRepository):
        self.users = users

    def register(self, request: UserRegisterRequest) -> User:
        if self.users.get_by_email(request.email) is not None:
            raise AlreadyExistsError("email has already been used")

        return self.users.create(
            email=request.email,
            password_hash=hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
        )

    def login(self, request: UserLoginRequest) -> UserLoginResponse:
        user = self.users.get_by_email(request.email)
        # Same message for unknown email and wrong password, so emails can't be probed
        if user is None or not verify_password(request.password, user.password or ""):
            raise AuthenticationError("email or password is invalid")

        token = TokenPair(
            access=create_token(TokenType.ACCESS, user.id),
            refresh=create_token(TokenType.REFRESH, user.id),
        )
        self.users.upsert_token(user.id, token.access, token.refresh)
        return UserLoginResponse(user=UserResponse.model_validate(user), token=token)

    def refresh_token(self, refresh_token: str) -> UserLoginResponse:
        claims, session = self._find_session(refresh_token)

        # New access token; the new refresh token keeps the original expiry,
        # so a session can't be extended forever by refreshing
        token = TokenPair(
            access=create_token(TokenType.ACCESS, claims.user_id),
            refresh=create_token(TokenType.REFRESH, claims.user_id, expires_at=claims.expires_at),
        )
        self.users.upsert_token(claims.user_id, token.access, token.refresh)
        return UserLoginResponse(user=UserResponse.model_validate(session.user), token=token)

    def logout(self, refresh_token: str) -> None:
        claims, _ = self._find_session(refresh_token)
        self.users.delete_token(claims.user_id)

    def authenticate(self, access_token: str) -> AuthContext:
        claims = parse_token(access_token, TokenType.ACCESS)

        # The token must also match the stored session, so logout / re-login revokes it
        session = self.users.get_token_by_access(claims.user_id, access_token)
        if session is None or session.user is None:
            raise AuthenticationError("user token not found")

        return AuthContext(user=session.user, permission=self.users.get_permission(claims.user_id))

    def _find_session(self, refresh_token: str) -> tuple[TokenClaims, UserToken]:
        claims = parse_token(refresh_token, TokenType.REFRESH)

        session = self.users.get_token_by_user_id(claims.user_id)
        if session is None or session.user is None or session.refresh != refresh_token:
            raise AuthenticationError("user token not found")
        return claims, session
