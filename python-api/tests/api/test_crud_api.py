import pytest

from app.core.database import SessionLocal
from app.models import User, UserPermission
from tests.api.helpers import assert_error

TOTAL_USERS = 25  # alice (from auth_headers) + 24 seeded


@pytest.fixture
def seeded(auth_headers):
    """24 more users (ids 2..25) and two permissions."""
    with SessionLocal() as db:
        db.add_all(
            User(
                email=f"user{i:02}@example.com",
                password="bcrypt-hash",
                first_name="Even" if i % 2 == 0 else "Odd",
                last_name=f"N{i}",
            )
            for i in range(2, TOTAL_USERS + 1)
        )
        db.add_all(
            [
                UserPermission(user_id=1, permission="admin"),
                UserPermission(user_id=2, permission="viewer"),
            ]
        )
        db.commit()
    return auth_headers


class TestAccess:
    def test_requires_login(self, client):
        assert_error(client.get("/api/v1/data/users/"), 401, "middlware-002", "token is missing")

    def test_unknown_model_returns_404(self, client, auth_headers):
        response = client.get("/api/v1/data/nope/", headers=auth_headers)

        assert_error(response, 404, "crud-001", "entity model not found")

    def test_user_tokens_are_not_exposed(self, client, auth_headers):
        response = client.get("/api/v1/data/user-tokens/", headers=auth_headers)

        assert_error(response, 404, "crud-001", "entity model not found")


class TestList:
    def test_default_page_has_real_totals(self, client, seeded):
        body = client.get("/api/v1/data/users/", headers=seeded).json()

        assert len(body["data"]) == 10
        assert (body["page"], body["page_size"]) == (1, 10)
        assert (body["total_data"], body["total_page"]) == (TOTAL_USERS, 3)
        assert body["data_schema"]["name"] == "users"

    def test_last_page_ordered_by_id(self, client, seeded):
        body = client.get("/api/v1/data/users/?_page=3", headers=seeded).json()

        assert [record["id"] for record in body["data"]] == [21, 22, 23, 24, 25]

    def test_never_returns_password(self, client, seeded):
        body = client.get("/api/v1/data/users/?_pageSize=100", headers=seeded).json()

        assert len(body["data"]) == TOTAL_USERS
        assert all("password" not in record for record in body["data"])

    def test_works_without_trailing_slash(self, client, seeded):
        response = client.get("/api/v1/data/users", headers=seeded, follow_redirects=False)

        assert response.status_code == 200
        assert response.json()["total_data"] == TOTAL_USERS

    def test_filters_with_pagination(self, client, seeded):
        response = client.get(
            "/api/v1/data/users/",
            params={"first_name": "Odd", "_pageSize": 5, "_page": 3},
            headers=seeded,
        )

        body = response.json()
        assert body["total_data"] == 12  # ids 3, 5, ..., 25
        assert body["total_page"] == 3
        assert len(body["data"]) == 2
        assert all(record["first_name"] == "Odd" for record in body["data"])

    def test_filters_by_exact_email(self, client, seeded):
        body = client.get(
            "/api/v1/data/users/", params={"email": "user07@example.com"}, headers=seeded
        ).json()

        assert [record["id"] for record in body["data"]] == [7]

    def test_filters_user_permissions(self, client, seeded):
        body = client.get("/api/v1/data/user-permissions/?user_id=2", headers=seeded).json()

        assert body["total_data"] == 1
        assert body["data"][0]["permission"] == "viewer"

    @pytest.mark.parametrize(
        ("query", "trace_id", "message"),
        [
            ("password=x", "crud-001", "cannot filter by 'password'"),
            ("id=abc", "crud-001", "invalid value for 'id'"),
            ("id=99999999999999999999", "crud-001", "invalid value for 'id'"),
            ("_page=abc", "middlware-003", "_page"),
            ("_page=99999999999999999999", "middlware-003", "_page"),
        ],
    )
    def test_invalid_query_returns_400(self, client, seeded, query, trace_id, message):
        response = client.get(f"/api/v1/data/users/?{query}", headers=seeded)

        assert_error(response, 400, trace_id, message)


class TestGet:
    def test_returns_record_without_password(self, client, seeded):
        response = client.get("/api/v1/data/users/5", headers=seeded)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["email"] == "user05@example.com"
        assert "password" not in data

    def test_missing_record_returns_404(self, client, seeded):
        response = client.get("/api/v1/data/users/999", headers=seeded)

        assert_error(response, 404, "crud-001", "record not found")

    @pytest.mark.parametrize("record_id", ["abc", "0", "99999999999999999999"])
    def test_invalid_id_returns_400(self, client, seeded, record_id):
        response = client.get(f"/api/v1/data/users/{record_id}", headers=seeded)

        assert_error(response, 400, "middlware-003", "record_id")


class TestDescribe:
    def test_describes_user_permissions(self, client, auth_headers):
        response = client.get("/api/v1/data/user-permissions/describe", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == {
            "type": "record",
            "name": "user-permissions",
            "fields": [
                {"name": "id", "type": "int"},
                {"name": "user_id", "type": "int"},
                {"name": "permission", "type": "string"},
                {"name": "updated_at", "type": "datetime"},
            ],
        }
