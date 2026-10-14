import math
from datetime import datetime
from typing import Any, get_args

from pydantic import BaseModel

from app.crud_registry import CrudResource
from app.domain.exceptions import InvalidRequestError, NotFoundError
from app.domain.repositories import CrudRepository
from app.domain.schemas.crud import DataListResponse, DataResponse

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 1000
MAX_BIGINT = 2**63 - 1  # Postgres bigint upper bound

_SCHEMA_TYPE_NAMES = {int: "int", str: "string", bool: "boolean", float: "double", datetime: "datetime"}


class CrudUsecase:
    def __init__(self, repository: CrudRepository, registry: dict[str, CrudResource]):
        self.repository = repository
        self.registry = registry

    def describe(self, slug: str) -> dict[str, Any]:
        return _describe_schema(self._resource(slug))

    def get(self, slug: str, record_id: int) -> DataResponse:
        resource = self._resource(slug)
        record = self.repository.get_by_id(resource.model, record_id)
        if record is None:
            raise NotFoundError("record not found")

        return DataResponse(
            data=_serialize(resource, record), data_schema=_describe_schema(resource)
        )

    def list(
        self, slug: str, page: int, page_size: int, filters: dict[str, str]
    ) -> DataListResponse:
        resource = self._resource(slug)

        # Same clamping rules as the Go app
        page = max(page, 1)
        page_size = DEFAULT_PAGE_SIZE if page_size < 1 else min(page_size, MAX_PAGE_SIZE)

        records, total = self.repository.list(
            resource.model,
            offset=(page - 1) * page_size,
            limit=page_size,
            filters=_parse_filters(resource, filters),
        )
        return DataListResponse(
            data=[_serialize(resource, record) for record in records],
            page=page,
            page_size=page_size,
            total_page=math.ceil(total / page_size),
            total_data=total,
            data_schema=_describe_schema(resource),
        )

    def _resource(self, slug: str) -> CrudResource:
        resource = self.registry.get(slug)
        if resource is None:
            raise NotFoundError("entity model not found")
        return resource


def _serialize(resource: CrudResource, record: Any) -> dict[str, Any]:
    return resource.schema.model_validate(record).model_dump(mode="json")


def _parse_filters(resource: CrudResource, filters: dict[str, str]) -> dict[str, Any]:
    """Allow only whitelisted columns, and convert query-string values to the column's type."""
    parsed = {}
    for field, raw_value in filters.items():
        if field not in resource.filterable:
            raise InvalidRequestError(
                f"cannot filter by '{field}', allowed: {', '.join(resource.filterable)}"
            )
        python_type = resource.model.__table__.c[field].type.python_type
        try:
            value = python_type(raw_value)
        except ValueError:
            value = None
        if value is None or (python_type is int and not -MAX_BIGINT <= value <= MAX_BIGINT):
            raise InvalidRequestError(f"invalid value for '{field}': {raw_value!r}")
        parsed[field] = value
    return parsed


def _describe_schema(resource: CrudResource) -> dict[str, Any]:
    """Avro-like description of the fields the API returns for this model."""
    return {
        "type": "record",
        "name": resource.slug,
        "fields": [
            {"name": name, "type": _type_name(field.annotation)}
            for name, field in resource.schema.model_fields.items()
        ],
    }


def _type_name(annotation: Any) -> str:
    # `int | None` -> int
    inner = [arg for arg in get_args(annotation) if arg is not type(None)] or [annotation]
    if isinstance(inner[0], type) and issubclass(inner[0], BaseModel):
        return inner[0].__name__
    return _SCHEMA_TYPE_NAMES.get(inner[0], "unknown")
