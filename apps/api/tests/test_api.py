from fastapi.testclient import TestClient

from gaitmate_api.main import app


def test_health_response() -> None:
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["service"] == "gaitmate-api"
    assert response.json()["data"]["timestamp"].endswith("Z")
