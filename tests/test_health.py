import pytest
from fastapi import status


def test_health_endpoint(client):
    """Test the health check endpoint returns 200 and correct response."""
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "service" in data
    assert data["service"] == "binance-endpoints"


def test_health_endpoint_response_format(client):
    """Test that health endpoint returns the expected JSON structure."""
    response = client.get("/health")
    data = response.json()

    # Check required fields
    required_fields = ["status", "timestamp", "service", "version"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Check data types
    assert isinstance(data["status"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["service"], str)
    assert isinstance(data["version"], str)
