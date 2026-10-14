import pytest

from app.crud_registry import CRUD_REGISTRY
from app.domain.exceptions import InvalidRequestError, NotFoundError
from app.models import User
from app.usecases.crud_usecase import CrudUsecase
from tests.unit.fakes import FakeCrudRepository


def make_users(count: int) -> list[User]:
    return [
        User(
            id=i,
            email=f"user{i:02}@example.com",
            password="bcrypt-hash",
            first_name="Even" if i % 2 == 0 else "Odd",
            last_name=f"N{i}",
        )
        for i in range(1, count + 1)
    ]


@pytest.fixture
def repo() -> FakeCrudRepository:
    return FakeCrudRepository(make_users(25))


@pytest.fixture
def usecase(repo) -> CrudUsecase:
    return CrudUsecase(repo, CRUD_REGISTRY)


class TestRegistry:
    def test_user_tokens_are_not_exposed(self, usecase):
        assert "user-tokens" not in CRUD_REGISTRY
        with pytest.raises(NotFoundError, match="entity model not found"):
            usecase.list("user-tokens", 1, 10, {})

    def test_unknown_slug(self, usecase):
        with pytest.raises(NotFoundError, match="entity model not found"):
            usecase.get("nope", 1)


class TestList:
    def test_paginates_with_real_total(self, usecase):
        result = usecase.list("users", page=3, page_size=10, filters={})

        assert [record["id"] for record in result.data] == [21, 22, 23, 24, 25]
        assert result.total_data == 25
        assert result.total_page == 3

    @pytest.mark.parametrize(
        ("page", "page_size", "expected_page", "expected_size", "expected_offset"),
        [
            (0, 0, 1, 10, 0),
            (-5, -1, 1, 10, 0),
            (2, 5000, 2, 1000, 1000),
            (3, 5, 3, 5, 10),
        ],
    )
    def test_clamps_page_and_page_size(
        self, usecase, repo, page, page_size, expected_page, expected_size, expected_offset
    ):
        result = usecase.list("users", page, page_size, {})

        assert (result.page, result.page_size) == (expected_page, expected_size)
        assert repo.last_list_call["offset"] == expected_offset
        assert repo.last_list_call["limit"] == expected_size

    def test_never_returns_password(self, usecase):
        result = usecase.list("users", 1, 100, {})

        assert result.data
        assert all("password" not in record for record in result.data)

    def test_filter_values_are_converted_to_column_type(self, usecase, repo):
        result = usecase.list("users", 1, 10, {"id": "3"})

        assert repo.last_list_call["filters"] == {"id": 3}
        assert [record["id"] for record in result.data] == [3]

    def test_filter_and_total(self, usecase):
        result = usecase.list("users", 1, 5, {"first_name": "Even"})

        assert result.total_data == 12
        assert result.total_page == 3
        assert all(record["first_name"] == "Even" for record in result.data)

    def test_rejects_filter_on_non_whitelisted_field(self, usecase):
        with pytest.raises(InvalidRequestError, match="cannot filter by 'password'"):
            usecase.list("users", 1, 10, {"password": "x"})

    @pytest.mark.parametrize("value", ["abc", str(2**63)])
    def test_rejects_invalid_filter_value(self, usecase, value):
        with pytest.raises(InvalidRequestError, match="invalid value for 'id'"):
            usecase.list("users", 1, 10, {"id": value})


class TestGet:
    def test_returns_record_without_password(self, usecase):
        result = usecase.get("users", 5)

        assert result.data["email"] == "user05@example.com"
        assert "password" not in result.data
        assert result.data_schema["name"] == "users"

    def test_missing_record(self, usecase):
        with pytest.raises(NotFoundError, match="record not found"):
            usecase.get("users", 999)


class TestDescribe:
    def test_lists_response_fields_with_types(self, usecase):
        schema = usecase.describe("users")

        assert schema["type"] == "record"
        assert schema["name"] == "users"
        assert schema["fields"] == [
            {"name": "id", "type": "int"},
            {"name": "email", "type": "string"},
            {"name": "first_name", "type": "string"},
            {"name": "last_name", "type": "string"},
            {"name": "created_at", "type": "datetime"},
            {"name": "updated_at", "type": "datetime"},
        ]
