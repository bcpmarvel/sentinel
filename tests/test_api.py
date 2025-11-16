import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from sentinel.api.app import app


@pytest.fixture
def client():
    test_client = TestClient(app)
    app.state.device = "cpu"
    app.state.detection_service = Mock()
    return test_client


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["device"] == "cpu"
