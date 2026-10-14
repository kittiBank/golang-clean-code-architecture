"""seed default user

Creates a test login: user@example.com / 123456.
Skipped if that email already exists, so it is safe on a DB that already has data.

Revision ID: 264b73fc5576
Revises: 642110effb1f
Create Date: 2026-10-14 16:39:32.506045

"""
from typing import Sequence, Union

import bcrypt
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '264b73fc5576'
down_revision: Union[str, Sequence[str], None] = '642110effb1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SEED_EMAIL = "user@example.com"
SEED_PASSWORD = "123456"


def upgrade() -> None:
    """Upgrade schema."""
    password_hash = bcrypt.hashpw(SEED_PASSWORD.encode(), bcrypt.gensalt(rounds=10)).decode()
    op.get_bind().execute(
        sa.text(
            """
            INSERT INTO users (email, password, first_name, last_name, created_at, updated_at)
            VALUES (:email, :password, 'Default', 'User', now(), now())
            ON CONFLICT (email) DO NOTHING
            """
        ),
        {"email": SEED_EMAIL, "password": password_hash},
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.get_bind().execute(sa.text("DELETE FROM users WHERE email = :email"), {"email": SEED_EMAIL})
