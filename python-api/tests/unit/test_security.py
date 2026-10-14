import time

import jwt
import pytest

from app.core.security import (
    TokenType,
    create_token,
    hash_password,
    parse_token,
    verify_password,
)
from app.domain.exceptions import AuthenticationError

SECRET = "test-secret-key-that-is-long-enough-for-hs256"  # from tests/conftest.py


def decode_unverified(token: str) -> dict:
    return jwt.decode(token, options={"verify_signature": False})


class TestPassword:
    def test_hash_then_verify(self):
        password_hash = hash_password("secret123")

        assert password_hash != "secret123"
        assert verify_password("secret123", password_hash)
        assert not verify_password("wrong", password_hash)

    def test_accepts_go_style_2a_hashes(self):
        # Go's bcrypt writes "$2a$" hashes; users registered by the Go app must still log in
        go_hash = hash_password("secret123").replace("$2b$", "$2a$", 1)

        assert verify_password("secret123", go_hash)

    @pytest.mark.parametrize("bad_hash", ["", "not-a-bcrypt-hash"])
    def test_malformed_hash_never_matches(self, bad_hash):
        assert not verify_password("secret123", bad_hash)

    def test_password_over_72_bytes_never_matches(self):
        assert not verify_password("a" * 73, hash_password("a" * 72))


class TestCreateToken:
    def test_payload_matches_go_format(self):
        payload = decode_unverified(create_token(TokenType.ACCESS, 42))

        assert payload["claims"] == {"id": 42}
        assert payload["iss"] == "golang-first-api-app"  # spaces replaced (Go bug fixed)
        assert payload["sub"] == "access-token"
        assert payload["aud"] == ["user", "admin"]

    @pytest.mark.parametrize(
        ("token_type", "lifetime"),
        [(TokenType.ACCESS, 86400), (TokenType.REFRESH, 172800)],  # refresh uses its own setting
    )
    def test_lifetime_comes_from_settings(self, token_type, lifetime):
        payload = decode_unverified(create_token(token_type, 1))

        assert payload["exp"] - payload["iat"] == lifetime

    def test_explicit_expiry_is_kept(self):
        expires_at = int(time.time()) + 500

        assert parse_token(create_token(TokenType.REFRESH, 1, expires_at), TokenType.REFRESH).expires_at == expires_at


class TestParseToken:
    def test_valid_token_returns_claims(self):
        claims = parse_token(create_token(TokenType.ACCESS, 7), TokenType.ACCESS)

        assert claims.user_id == 7

    def test_expired(self):
        token = create_token(TokenType.ACCESS, 1, expires_at=int(time.time()) - 10)

        with pytest.raises(AuthenticationError, match="token had expired"):
            parse_token(token, TokenType.ACCESS)

    def test_wrong_signature(self):
        payload = decode_unverified(create_token(TokenType.ACCESS, 1))
        forged = jwt.encode(payload, "another-secret-that-is-also-long-enough", algorithm="HS256")

        with pytest.raises(AuthenticationError, match="Signature verification failed"):
            parse_token(forged, TokenType.ACCESS)

    def test_garbage(self):
        with pytest.raises(AuthenticationError, match="token format is invalid"):
            parse_token("not-a-jwt", TokenType.ACCESS)

    @pytest.mark.parametrize(
        ("issued", "expected"),
        [(TokenType.REFRESH, TokenType.ACCESS), (TokenType.ACCESS, TokenType.REFRESH)],
    )
    def test_wrong_token_type(self, issued, expected):
        with pytest.raises(AuthenticationError, match="token type is invalid"):
            parse_token(create_token(issued, 1), expected)

    def test_missing_user_claims(self):
        payload = decode_unverified(create_token(TokenType.ACCESS, 1))
        del payload["claims"]
        token = jwt.encode(payload, SECRET, algorithm="HS256")

        with pytest.raises(AuthenticationError, match="parse token failed"):
            parse_token(token, TokenType.ACCESS)
