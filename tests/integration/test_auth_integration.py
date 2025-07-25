from fastapi.testclient import TestClient

from src.presentation.main import app

client = TestClient(app)


def test_register_and_login(clean_database):
    """Test user registration and login flow"""
    # Register user
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "password123",
        },
    )
    assert response.status_code == 200  # Registration devuelve 200, no 201

    # Login user - OAuth2PasswordRequestForm usa 'username' no 'email'
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",  # username, no email
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_me_endpoint(clean_database):
    """Test /me endpoint with authentication"""
    # First register and login
    client.post(
        "/api/auth/register",
        json={
            "email": "me@example.com",
            "full_name": "Me User",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "me@example.com",  # username, no email
            "password": "password123",
        },
    )
    token = login_response.json()["access_token"]

    # Test /me endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["full_name"] == "Me User"
