"""API tests run against a real Postgres: a throwaway database built with Alembic."""

from pathlib import Path

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine
from app.main import app
from tests.api.helpers import bearer, login, register

ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


def _connect_admin() -> psycopg.Connection:
    settings = get_settings()
    return psycopg.connect(
        host=settings.postgres_db_host,
        port=settings.postgres_db_port,
        user=settings.postgres_db_user,
        password=settings.postgres_db_password,
        dbname="postgres",
        autocommit=True,
        connect_timeout=3,
    )


@pytest.fixture(scope="session", autouse=True)
def test_database():
    name = get_settings().postgres_db_name
    assert name.endswith("_test"), f"refusing to recreate non-test database {name!r}"

    try:
        admin = _connect_admin()
    except psycopg.OperationalError as exc:
        pytest.skip(f"Postgres is not reachable, start it with `docker compose up -d` ({exc})")

    with admin:
        admin.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
        admin.execute(f'CREATE DATABASE "{name}"')
    command.upgrade(Config(str(ALEMBIC_INI)), "head")  # also proves the migrations run

    yield

    engine.dispose()
    with _connect_admin() as admin:
        admin.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')


@pytest.fixture(autouse=True)
def clean_tables():
    """Every test starts with empty tables (ids restart at 1)."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE users, user_tokens, user_permissions RESTART IDENTITY CASCADE"))


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_headers(client) -> dict[str, str]:
    """A registered, logged-in user (alice@example.com, id 1)."""
    register(client)
    return bearer(login(client)["access"])
