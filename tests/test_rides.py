import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def rider_auth_headers():
    """Create rider and return auth headers"""
    user_data = {
        "email": "rider_test@example.com",
        "password": "TestPass123",
        "full_name": "Test Rider",
        "role": "rider"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def driver_auth_headers():
    """Create driver and return auth headers"""
    user_data = {
        "email": "driver_test@example.com",
        "password": "TestPass123",
        "full_name": "Test Driver",
        "role": "driver"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_ride_data():
    return {
        "pickup": {
            "lat": 40.7128,
            "lon": -74.0060
        },
        "dropoff": {
            "lat": 40.7589,
            "lon": -73.9851
        },
        "pickup_address": "123 Main St, New York, NY",
        "dropoff_address": "456 Broadway, New York, NY",
        "price": 25.50,
        "estimated_duration": 30,
        "notes": "Test ride"
    }

def test_create_ride(rider_auth_headers, sample_ride_data):
    """Test ride creation by rider"""
    response = client.post(
        "/api/v1/rides/",
        json=sample_ride_data,
        headers=rider_auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["price"] == sample_ride_data["price"]
    assert "id" in data
    assert "created_at" in data

def test_unauthorized_ride_creation(sample_ride_data):
    """Test ride creation without authentication"""
    response = client.post("/api/v1/rides/", json=sample_ride_data)
    assert response.status_code == 401

def test_get_available_rides(driver_auth_headers, rider_auth_headers, sample_ride_data):
    """Test getting available rides by driver"""
    # Create a ride first
    client.post(
        "/api/v1/rides/",
        json=sample_ride_data,
        headers=rider_auth_headers
    )
    
    # Get available rides as driver
    response = client.get(
        "/api/v1/rides/available",
        headers=driver_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert data[0]["status"] == "pending"

def test_ride_validation():
    """Test ride input validation"""
    invalid_data = {
        "pickup": {
            "lat": 200,  # Invalid latitude
            "lon": -74.0060
        },
        "dropoff": {
            "lat": 40.7589,
            "lon": -300  # Invalid longitude
        },
        "price": -10,  # Negative price
    }
    
    user_data = {
        "email": "validation_test@example.com",
        "password": "TestPass123",
        "full_name": "Test User",
        "role": "rider"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/v1/rides/", json=invalid_data, headers=headers)
    assert response.status_code == 422
