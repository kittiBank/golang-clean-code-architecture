"""Password hashing (bcrypt) and JWT signing/parsing (HS256)."""

import time
from dataclasses import dataclass
from enum import StrEnum

import bcrypt
import jwt

from app.core.config import get_settings
from app.domain.exceptions import AuthenticationError

ALGORITHM = "HS256"
AUDIENCE = ["user", "admin"]
BCRYPT_ROUNDS = 10  # same cost as the Go app, so existing hashes stay compatible


class TokenType(StrEnum):
    ACCESS = "access-token"
    REFRESH = "refresh-token"


@dataclass(frozen=True)
class TokenClaims:
    user_id: int
    expires_at: int  # unix timestamp


# --- Password ---


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:  # malformed hash or password longer than bcrypt's 72-byte limit
        return False


# --- JWT ---


def _issuer() -> str:
    # The Go app meant to do this but discarded the replace result
    return get_settings().name.lower().replace(" ", "-")


def create_token(token_type: TokenType, user_id: int, expires_at: int | None = None) -> str:
    """Sign a token. Pass `expires_at` to keep an existing expiry (used when rotating refresh tokens)."""
    settings = get_settings()
    now = int(time.time())
    if expires_at is None:
        lifetime = (
            settings.jwt_access_expires
            if token_type is TokenType.ACCESS
            else settings.jwt_refresh_expires
        )
        expires_at = now + lifetime

    payload = {
        "claims": {"id": user_id},
        "iss": _issuer(),
        "sub": token_type.value,
        "aud": AUDIENCE,
        "exp": expires_at,
        "nbf": now,
        "iat": now,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def parse_token(token: str, expected_type: TokenType) -> TokenClaims:
    """Verify signature, expiry, issuer, audience and token type. Raises AuthenticationError."""
    try:
        payload = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=[ALGORITHM],
            audience="user",
            issuer=_issuer(),
            options={"require": ["exp", "sub", "claims"]},
        )
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("token had expired")
    except jwt.InvalidSignatureError as exc:
        raise AuthenticationError(f"parse token failed: {exc}")
    except jwt.DecodeError:
        raise AuthenticationError("token format is invalid")
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError(f"parse token failed: {exc}")

    if payload["sub"] != expected_type.value:
        raise AuthenticationError("token type is invalid")
    try:
        user_id = int(payload["claims"]["id"])
    except (KeyError, TypeError, ValueError):
        raise AuthenticationError("claims type is invalid")

    return TokenClaims(user_id=user_id, expires_at=payload["exp"])
