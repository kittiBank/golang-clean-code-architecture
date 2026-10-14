"""Models exposed through the generic CRUD API (/api/v1/data/{slug}).

Only registered models are reachable, and only the fields of their `schema` are returned.
To expose a new table, add a CrudResource here.
"""

from dataclasses import dataclass

from pydantic import BaseModel

from app.core.database import Base
from app.domain.schemas.user import UserPermissionResponse, UserResponse
from app.models import User, UserPermission


@dataclass(frozen=True)
class CrudResource:
    model: type[Base]
    schema: type[BaseModel]  # response shape: fields not listed here are never returned
    filterable: tuple[str, ...] = ()  # columns allowed as ?field=value filters

    @property
    def slug(self) -> str:
        return self.model.__tablename__.replace("_", "-")


CRUD_RESOURCES = [
    CrudResource(User, UserResponse, filterable=("id", "email", "first_name", "last_name")),
    CrudResource(UserPermission, UserPermissionResponse, filterable=("id", "user_id", "permission")),
    # user_tokens is intentionally not registered: it holds every user's live access/refresh tokens
]

CRUD_REGISTRY: dict[str, CrudResource] = {resource.slug: resource for resource in CRUD_RESOURCES}
