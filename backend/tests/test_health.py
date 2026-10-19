from __future__ import annotations

from app import create_app
from helpers.errors import AppError


def test_health_reports_database_and_migration(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert data["migration"]


def test_health_returns_503_when_database_is_down(client, monkeypatch):
    def broken_session():
        raise ConnectionError("database down")

    monkeypatch.setattr("routes.health.get_ro_session", broken_session)

    response = client.get("/api/health")

    assert response.status_code == 503
    assert response.get_json()["error"]["code"] == "DATABASE_UNAVAILABLE"


def test_unknown_route_returns_json_404(client):
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "NOT_FOUND"


def test_app_error_uses_the_envelope():
    # Fresh app: routes cannot be added to the shared one after it has served requests.
    app = create_app()

    @app.get("/api/_test/app-error")
    def raise_app_error():
        raise AppError("BOOKING_DATES_TAKEN", "Those dates are taken.", 409, {"listing_id": 1})

    response = app.test_client().get("/api/_test/app-error")

    assert response.status_code == 409
    assert response.get_json() == {
        "error": {
            "code": "BOOKING_DATES_TAKEN",
            "message": "Those dates are taken.",
            "details": {"listing_id": 1},
        }
    }
