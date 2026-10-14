from fastapi.testclient import TestClient
from httpx import Response

EMAIL = "alice@example.com"
PASSWORD = "secret123"


def register(client: TestClient, email: str = EMAIL, password: str = PASSWORD, **fields) -> Response:
    return client.post(
        "/api/v1/users/register", json={"email": email, "password": password, **fields}
    )


def login(client: TestClient, email: str = EMAIL, password: str = PASSWORD) -> dict[str, str]:
    """Log in and return {"access": ..., "refresh": ...}."""
    response = client.post("/api/v1/users/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["token"]


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def assert_error(response: Response, status: int, trace_id: str, message: str | None = None):
    assert response.status_code == status, response.text
    body = response.json()
    assert body["trace_id"] == trace_id
    if message is not None:
        assert message in body["message"]
