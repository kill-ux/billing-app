from flask_sqlalchemy.model import _QueryProperty
import pytest
from pytest_mock import MockerFixture
# from server import app as flask_app, db

    
@pytest.fixture
def app(monkeypatch, mocker: MockerFixture):
    monkeypatch.setenv("BILLING_DB_USER", "billing")
    monkeypatch.setenv("BILLING_DB_PASS", "billing")
    monkeypatch.setenv("BILLING_DB_NAME", "billing")
    monkeypatch.setenv("BILLING_DB_HOST", "billing-db")
    monkeypatch.setenv("BILLING_APP_PORT", "5000")
    
    monkeypatch.setenv("RABBITMQ_USER", "rabbitmq")
    monkeypatch.setenv("RABBITMQ_PASS", "rabbitmq")
    monkeypatch.setenv("RABBITMQ_HOST", "rabbitmq")
    monkeypatch.setenv("RABBITMQ_PORT", "5672")
    monkeypatch.setenv("RABBITMQ_QUEUE", "rabbitmq")

    mocker.patch("server.db.create_all")
    mocker.patch("server.threading.Thread")
    mocker.patch("server.db.session.execute")
    mocker.patch("server.consume_and_store_order")
    mocker.patch("server.init_app_services")

    from server import app as test_app
    return test_app

@pytest.fixture
def client(app):
    with app.app_context():
        yield app.test_client()

@pytest.fixture
def fake_upstream_response(mocker):
    resp = mocker.Mock()
    resp.content = b"{}"
    resp.status_code = 200
    resp.headers = {"Content-Type": "application/json"}
    return resp

@pytest.fixture
def movie_data():
    """
    {
        "id": 1,
        "title": "Test Movie",
        "description": "A test movie.",
    }
    """
    return {
        "id": 1,
        "title": "Test Movie",
        "description": "A test movie.",
    }
