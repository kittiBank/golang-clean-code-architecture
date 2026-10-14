from typing import Any

from pydantic import BaseModel


class DataResponse(BaseModel):
    code: int = 200
    data: dict[str, Any]
    message: str = ""
    data_schema: dict[str, Any]


class DataListResponse(BaseModel):
    code: int = 200
    data: list[dict[str, Any]]
    page: int
    page_size: int
    total_page: int
    total_data: int
    message: str = ""
    data_schema: dict[str, Any]
