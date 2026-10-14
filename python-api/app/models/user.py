"""User tables. Column, index and FK names match the schema GORM created in the Go app."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("idx_users_email", "email", unique=True),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str | None] = mapped_column(Text)
    first_name: Mapped[str | None] = mapped_column(Text)
    last_name: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    password: Mapped[str | None] = mapped_column(Text)  # bcrypt hash, never returned by the API


class UserToken(Base):
    """The user's current session: one row per user, replaced on every login."""

    __tablename__ = "user_tokens"
    __table_args__ = (Index("idx_user_tokens_user_id", "user_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id", name="fk_user_tokens_user", onupdate="CASCADE", ondelete="SET NULL"
        ),
    )
    access: Mapped[str | None] = mapped_column(Text)
    refresh: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    user: Mapped[User | None] = relationship()


class UserPermission(Base):
    __tablename__ = "user_permissions"
    __table_args__ = (Index("idx_user_permissions_user_id", "user_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id", name="fk_user_permissions_user", onupdate="CASCADE", ondelete="SET NULL"
        ),
    )
    permission: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    user: Mapped[User | None] = relationship()
