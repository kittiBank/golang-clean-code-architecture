# Import every model here so Base.metadata knows all tables (used by Alembic).
from app.models.user import User, UserPermission, UserToken

__all__ = ["User", "UserPermission", "UserToken"]
