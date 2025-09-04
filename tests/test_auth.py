import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def sample_user_data():
    return {
        "email": "test@example.com",
        "password": "TestPass123",
        "full_name": "Test User",
        "role": "rider",
        "phone": "+1234567890"
    }

def test_user_registration(sample_user_data):
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == sample_user_data["email"]
    assert data["full_name"] == sample_user_data["full_name"]
    assert data["role"] == sample_user_data["role"]
    assert "id" in data
    assert "created_at" in data

def test_user_login(sample_user_data):
    """Test user login"""
    # First register the user
    client.post("/api/v1/auth/register", json=sample_user_data)
    
    # Then try to login
    login_data = {
        "email": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data

def test_invalid_login():
    """Test login with invalid credentials"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401

def test_registration_validation():
    """Test registration input validation"""
    invalid_data = {
        "email": "invalid-email",
        "password": "weak",
        "full_name": "",
        "role": "invalid_role"
    }
    response = client.post("/api/v1/auth/register", json=invalid_data)
    assert response.status_code == 422
