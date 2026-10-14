from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app

client = TestClient(app)


def test_health_check_returns_name_and_version():
    response = client.get("/api/v1/")

    assert response.status_code == 200
    settings = get_settings()
    assert response.json() == {"name": settings.name, "version": settings.version}


def test_unknown_route_returns_formatted_404():
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"trace_id": "middlware-001", "message": "router not found"}
