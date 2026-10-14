"""FastAPI dependencies: wire repositories into use cases, and authenticate requests."""

from typing import Annotated

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import JWT_AUTH_ERROR, AppError, domain_errors
from app.models import User
from app.repositories.user_repository import SqlAlchemyUserRepository
from app.usecases.user_usecase import AuthContext, UserUsecase

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_usecase(db: Annotated[Session, Depends(get_db)]) -> UserUsecase:
    return UserUsecase(SqlAlchemyUserRepository(db))


UserUsecaseDep = Annotated[UserUsecase, Depends(get_user_usecase)]


def get_auth_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    usecase: UserUsecaseDep,
) -> AuthContext:
    """Replaces the Go JwtAuth middleware: requires `Authorization: Bearer <access token>`."""
    if credentials is None:
        raise AppError(status.HTTP_401_UNAUTHORIZED, JWT_AUTH_ERROR, "token is missing")
    with domain_errors(JWT_AUTH_ERROR):
        return usecase.authenticate(credentials.credentials)


AuthContextDep = Annotated[AuthContext, Depends(get_auth_context)]


def get_current_user(auth: AuthContextDep) -> User:
    return auth.user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
