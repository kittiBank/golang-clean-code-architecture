from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from alembic.config import Config

import app.models  # noqa: F401  (registers all tables)
from app.core.database import Base, engine
from tests.api.conftest import ALEMBIC_INI


def test_database_is_at_latest_migration():
    head = ScriptDirectory.from_config(Config(str(ALEMBIC_INI))).get_current_head()

    with engine.connect() as conn:
        assert MigrationContext.configure(conn).get_current_revision() == head


def test_migrations_match_the_models():
    """Fails if a model changed without a matching Alembic migration."""
    with engine.connect() as conn:
        assert compare_metadata(MigrationContext.configure(conn), Base.metadata) == []
