from pytest_mock import MockerFixture

"""
Unit tests for the health check route in app/routes/health.py.
"""

def test_health_return_ok(client, mocker):
    mocker.patch("server.db.session.execute")

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "ok"
    assert data["services"]["database"] == "up"

def test_health_database_failure(client, mocker):
    mocker.patch(
        "server.db.session.execute",
        side_effect=Exception("database unavailable"),
    )

    response = client.get("/health")

    assert response.status_code == 503

    data = response.get_json()
    assert data["status"] == "error"
    assert data["services"]["database"] == "down"
    assert data["error"] == "database unavailable"