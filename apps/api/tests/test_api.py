from fastapi.testclient import TestClient

from gaitmate_api.main import create_app


def test_health_response() -> None:
    response = TestClient(create_app()).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["service"] == "gaitmate-api"
    assert response.json()["data"]["timestamp"].endswith("Z")
    assert response.headers["x-request-id"]


def test_not_found_uses_error_envelope() -> None:
    response = TestClient(create_app()).get("/api/v1/missing")
    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "NOT_FOUND", "message": "Not Found"},
        "request_id": response.headers["x-request-id"],
    }


def test_validation_error_omits_input_value() -> None:
    api = create_app()

    @api.get("/api/v1/test/validation")
    def validated(value: int) -> dict[str, int]:
        return {"value": value}

    response = TestClient(api).get("/api/v1/test/validation?value=private-value")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["details"][0]["field"] == "query.value"
    assert "private-value" not in response.text


def test_unexpected_error_is_safe_and_traceable() -> None:
    api = create_app()

    @api.get("/api/v1/test/error")
    def broken() -> None:
        raise RuntimeError("private details")

    response = TestClient(api).get(
        "/api/v1/test/error", headers={"Origin": "http://localhost:5173"}
    )
    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "INTERNAL_ERROR", "message": "Internal server error"},
        "request_id": response.headers["x-request-id"],
    }
    assert "private details" not in response.text
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
