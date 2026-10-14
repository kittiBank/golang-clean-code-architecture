import pytest

from app.core.security import TokenType, create_token, parse_token, verify_password
from app.domain.exceptions import AlreadyExistsError, AuthenticationError
from app.domain.schemas.user import UserLoginRequest, UserRegisterRequest
from app.models import UserPermission
from app.usecases.user_usecase import UserUsecase
from tests.unit.fakes import FakeUserRepository

EMAIL = "alice@example.com"
PASSWORD = "secret123"


@pytest.fixture
def repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def usecase(repo) -> UserUsecase:
    return UserUsecase(repo)


@pytest.fixture
def user(usecase):
    return usecase.register(
        UserRegisterRequest(email=EMAIL, password=PASSWORD, first_name="Alice", last_name="Doe")
    )


def login(usecase: UserUsecase, email: str = EMAIL, password: str = PASSWORD):
    return usecase.login(UserLoginRequest(email=email, password=password))


class TestRegister:
    def test_creates_user_with_hashed_password(self, user):
        assert user.email == EMAIL
        assert user.password != PASSWORD
        assert verify_password(PASSWORD, user.password)

    def test_duplicate_email_is_rejected(self, usecase, user):
        with pytest.raises(AlreadyExistsError, match="email has already been used"):
            usecase.register(UserRegisterRequest(email=EMAIL, password="other"))


class TestLogin:
    def test_returns_user_and_tokens_and_stores_session(self, usecase, repo, user):
        result = login(usecase)

        assert result.user.email == EMAIL
        assert parse_token(result.token.access, TokenType.ACCESS).user_id == user.id
        assert parse_token(result.token.refresh, TokenType.REFRESH).user_id == user.id
        assert repo.tokens[user.id].access == result.token.access
        assert repo.tokens[user.id].refresh == result.token.refresh

    @pytest.mark.parametrize(
        ("email", "password"),
        [(EMAIL, "wrong-password"), ("ghost@example.com", PASSWORD)],
        ids=["wrong-password", "unknown-email"],
    )
    def test_bad_credentials_give_the_same_error(self, usecase, user, email, password):
        with pytest.raises(AuthenticationError, match="email or password is invalid"):
            login(usecase, email, password)

    def test_new_login_revokes_previous_session(self, usecase, user, clock):
        first = login(usecase)
        clock.advance(1)
        second = login(usecase)

        with pytest.raises(AuthenticationError, match="user token not found"):
            usecase.authenticate(first.token.access)
        assert usecase.authenticate(second.token.access).user.id == user.id


class TestRefreshToken:
    def test_issues_new_tokens_and_keeps_refresh_expiry(self, usecase, user, clock):
        first = login(usecase)
        clock.advance(1)
        refreshed = usecase.refresh_token(first.token.refresh)

        assert refreshed.user.id == user.id
        assert refreshed.token.access != first.token.access
        assert (
            parse_token(refreshed.token.refresh, TokenType.REFRESH).expires_at
            == parse_token(first.token.refresh, TokenType.REFRESH).expires_at
        )

    def test_revokes_old_access_token(self, usecase, user, clock):
        first = login(usecase)
        clock.advance(1)
        usecase.refresh_token(first.token.refresh)

        with pytest.raises(AuthenticationError, match="user token not found"):
            usecase.authenticate(first.token.access)

    def test_old_refresh_token_cannot_be_reused(self, usecase, user, clock):
        first = login(usecase)
        clock.advance(1)
        usecase.refresh_token(first.token.refresh)

        with pytest.raises(AuthenticationError, match="user token not found"):
            usecase.refresh_token(first.token.refresh)

    def test_rejects_access_token(self, usecase, user):
        with pytest.raises(AuthenticationError, match="token type is invalid"):
            usecase.refresh_token(login(usecase).token.access)


class TestLogout:
    def test_removes_session(self, usecase, repo, user):
        tokens = login(usecase).token

        usecase.logout(tokens.refresh)

        assert user.id not in repo.tokens
        with pytest.raises(AuthenticationError, match="user token not found"):
            usecase.authenticate(tokens.access)

    def test_second_logout_fails(self, usecase, user):
        tokens = login(usecase).token
        usecase.logout(tokens.refresh)

        with pytest.raises(AuthenticationError, match="user token not found"):
            usecase.logout(tokens.refresh)


class TestAuthenticate:
    def test_returns_user_and_permission(self, usecase, repo, user):
        repo.permissions[user.id] = UserPermission(user_id=user.id, permission="admin")

        auth = usecase.authenticate(login(usecase).token.access)

        assert auth.user.id == user.id
        assert auth.permission.permission == "admin"

    def test_permission_is_optional(self, usecase, user):
        assert usecase.authenticate(login(usecase).token.access).permission is None

    def test_signed_token_without_stored_session_is_rejected(self, usecase, user):
        token = create_token(TokenType.ACCESS, user.id)  # valid JWT, but never issued by login

        with pytest.raises(AuthenticationError, match="user token not found"):
            usecase.authenticate(token)

    def test_rejects_refresh_token(self, usecase, user):
        with pytest.raises(AuthenticationError, match="token type is invalid"):
            usecase.authenticate(login(usecase).token.refresh)
