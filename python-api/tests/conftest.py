"""Shared test setup.

Settings are forced here, before the app is imported, so tests never touch the dev
database and never depend on what is in your local .env.
"""

import os

os.environ["GOAPP_NAME"] = "GOLANG FIRST API APP"
os.environ["GOAPP_VERSION"] = "0.0.1"
os.environ["GOAPP_POSTGRES_DB_NAME"] = "fastapi_test"  # created and dropped by tests/api
os.environ["GOAPP_SECRET_KEY"] = "test-secret-key-that-is-long-enough-for-hs256"
os.environ["GOAPP_JWT_ACCESS_EXPIRES"] = "86400"
os.environ["GOAPP_JWT_REFRESH_EXPIRES"] = "172800"

import time  # noqa: E402

import pytest  # noqa: E402

from app.core import security  # noqa: E402


class FakeClock:
    """Stands in for the `time` module inside app.core.security."""

    def __init__(self, start: float):
        self.now = start

    def time(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock(monkeypatch) -> FakeClock:
    """Control token timestamps, e.g. so two logins in one test get different tokens.

    Starts a minute in the past: tokens must never be issued in the future,
    or PyJWT rejects them as "not yet valid" (nbf).
    """
    fake = FakeClock(start=time.time() - 60)
    monkeypatch.setattr(security, "time", fake)
    return fake
