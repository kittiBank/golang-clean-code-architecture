from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep, UserUsecaseDep
from app.core.errors import ErrorResponse, domain_errors
from app.domain.schemas.user import (
    UserLoginRequest,
    UserLoginResponse,
    UserRefreshTokenRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.models import User

# Trace ids kept from the Go handlers
REGISTER_USER_ERROR = "users-001"
LOGIN_USER_ERROR = "users-002"
REFRESH_TOKEN_ERROR = "users-003"
LOGOUT_USER_ERROR = "users-004"

router = APIRouter(
    prefix="/users",
    tags=["User"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    responses={409: {"model": ErrorResponse, "description": "Email already used"}},
)
def register_user(body: UserRegisterRequest, usecase: UserUsecaseDep) -> User:
    with domain_errors(REGISTER_USER_ERROR):
        return usecase.register(body)


@router.post("/login", response_model=UserLoginResponse, summary="User login")
def login_user(body: UserLoginRequest, usecase: UserUsecaseDep) -> UserLoginResponse:
    with domain_errors(LOGIN_USER_ERROR):
        return usecase.login(body)


@router.post("/refresh-token", response_model=UserLoginResponse, summary="Refresh user token")
def refresh_token(body: UserRefreshTokenRequest, usecase: UserUsecaseDep) -> UserLoginResponse:
    with domain_errors(REFRESH_TOKEN_ERROR):
        return usecase.refresh_token(body.refresh_token)


@router.post("/logout", response_model=None, summary="User logout")
def logout_user(body: UserRefreshTokenRequest, usecase: UserUsecaseDep) -> None:
    with domain_errors(LOGOUT_USER_ERROR):
        usecase.logout(body.refresh_token)


# GET is the RESTful form; POST is kept for compatibility with the Go API
@router.get("/profile", response_model=UserResponse, summary="Get user profile")
@router.post("/profile", response_model=UserResponse, summary="Get user profile (legacy POST)")
def get_user_profile(user: CurrentUserDep) -> User:
    return user
