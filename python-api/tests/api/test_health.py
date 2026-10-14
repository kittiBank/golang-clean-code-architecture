from fastapi.testclient import TestClient

from app.api.deps import get_user_usecase
from app.main import app
from tests.api.helpers import assert_error


def test_health_check_returns_name_and_version(client):
    response = client.get("/api/v1/")

    assert response.status_code == 200
    assert response.json() == {"name": "GOLANG FIRST API APP", "version": "0.0.1"}


def test_unknown_route_returns_formatted_404(client):
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"trace_id": "middlware-001", "message": "router not found"}


def test_wrong_method_returns_formatted_error(client):
    assert_error(client.delete("/api/v1/"), 405, "http-error", "Method Not Allowed")


def test_unexpected_error_returns_500_without_details():
    def broken_usecase():
        raise RuntimeError("database password is hunter2")

    app.dependency_overrides[get_user_usecase] = broken_usecase
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            "/api/v1/users/login", json={"email": "a@example.com", "password": "x"}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json() == {"trace_id": "internal-error", "message": "internal server error"}


def test_cors_allows_browser_frontends(client):
    response = client.options(
        "/api/v1/",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )

    assert response.headers["access-control-allow-origin"] == "*"
