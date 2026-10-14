from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, Request

from app.api.deps import CrudUsecaseDep, get_auth_context
from app.core.errors import ErrorResponse, domain_errors
from app.domain.schemas.crud import DataListResponse, DataResponse
from app.usecases.crud_usecase import DEFAULT_PAGE_SIZE, MAX_BIGINT, MAX_PAGE_SIZE

CRUD_ERROR = "crud-001"
PAGINATION_PARAMS = ("_page", "_pageSize")

router = APIRouter(
    prefix="/data",
    tags=["CRUD"],
    dependencies=[Depends(get_auth_context)],  # every CRUD route requires login
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Unknown model or record"},
    },
)


@router.get("/{slug}/describe", summary="Describe a model's fields")
def describe_model(slug: str, usecase: CrudUsecaseDep) -> dict[str, Any]:
    with domain_errors(CRUD_ERROR):
        return usecase.describe(slug)


@router.get(
    "/{slug}/",
    response_model=DataListResponse,
    summary="List records",
    description="Paginate with `_page` / `_pageSize`. Any other query param is an "
    "exact-match filter on a whitelisted field, e.g. `?email=alice@example.com`.",
)
@router.get("/{slug}", response_model=DataListResponse, include_in_schema=False)
def list_records(
    slug: str,
    request: Request,
    usecase: CrudUsecaseDep,
    page: Annotated[int, Query(alias="_page", le=MAX_BIGINT // MAX_PAGE_SIZE)] = 1,
    page_size: Annotated[int, Query(alias="_pageSize")] = DEFAULT_PAGE_SIZE,
) -> DataListResponse:
    filters = {
        key: value for key, value in request.query_params.items() if key not in PAGINATION_PARAMS
    }
    with domain_errors(CRUD_ERROR):
        return usecase.list(slug, page, page_size, filters)


@router.get("/{slug}/{record_id}", response_model=DataResponse, summary="Get one record by id")
def get_record(
    slug: str, record_id: Annotated[int, Path(ge=1, le=MAX_BIGINT)], usecase: CrudUsecaseDep
) -> DataResponse:
    with domain_errors(CRUD_ERROR):
        return usecase.get(slug, record_id)
