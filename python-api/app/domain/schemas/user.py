from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field


def _max_72_bytes(password: str) -> str:
    if len(password.encode()) > 72:
        raise ValueError("password must be at most 72 bytes")  # bcrypt limit
    return password


Password = Annotated[str, Field(min_length=1), AfterValidator(_max_72_bytes)]


# --- Requests ---


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: Password
    first_name: str = ""
    last_name: str = ""


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserRefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


# --- Responses ---


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str | None
    last_name: str | None
    created_at: datetime | None
    updated_at: datetime | None


class TokenPair(BaseModel):
    access: str
    refresh: str


class UserLoginResponse(BaseModel):
    user: UserResponse
    token: TokenPair
