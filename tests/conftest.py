import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_data():
    """Sample data for testing endpoints."""
    return {"symbol": "BTCUSDT", "interval": "1h", "limit": 100}
