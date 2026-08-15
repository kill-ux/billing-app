import pytest, os, requests

@pytest.fixture(scope="session")
def app_url():
    return os.getenv("APP_URL", "http://inventory-app:8000")

@pytest.fixture(scope="session")
def client(app_url):
    """Provide a requests session for testing."""
    session = requests.Session()
    yield session
    session.close()