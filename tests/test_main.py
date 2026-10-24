from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Verify that the health check endpoint returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "incubrix-content-engine"
    assert data["version"] == "0.1.0"


def test_root():
    """Verify that the root endpoint returns service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["health_url"] == "/health"
