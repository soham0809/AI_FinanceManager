"""
Test Authentication Endpoints
Comprehensive tests for user registration, login, token management
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.auth
class TestAuthRoutes:
    """Test authentication endpoints"""
    
    def test_register_new_user(self, client: TestClient):
        """Test POST /auth/register creates new user"""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["full_name"] == "New User"
        assert data["is_active"] is True
        assert "id" in data
    
    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with duplicate email fails"""
        response = client.post(
            "/auth/register",
            json={
                "email": test_user.email,
                "username": "differentusername",
                "password": "password123",
                "full_name": "Duplicate User"
            }
        )
        
        assert response.status_code == 400
    
    def test_register_duplicate_username(self, client: TestClient, test_user):
        """Test registration with duplicate username fails"""
        response = client.post(
            "/auth/register",
            json={
                "email": "different@example.com",
                "username": test_user.username,
                "password": "password123",
                "full_name": "Duplicate User"
            }
        )
        
        assert response.status_code == 400
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format"""
        response = client.post(
            "/auth/register",
            json={
                "email": "notanemail",
                "username": "testuser",
                "password": "password123",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_success(self, client: TestClient, test_user):
        """Test POST /auth/login with valid credentials"""
        response = client.post(
            "/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        assert data["user"]["email"] == test_user.email
    
    def test_login_wrong_password(self, client: TestClient, test_user):
        """Test login with incorrect password"""
        response = client.post(
            "/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, auth_headers, test_user):
        """Test GET /auth/me returns current user info"""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["id"] == test_user.id
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test GET /auth/me without authentication"""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test GET /auth/me with invalid token"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_update_current_user(self, client: TestClient, auth_headers, test_user):
        """Test PUT /auth/me updates user info"""
        response = client.put(
            "/auth/me",
            headers=auth_headers,
            json={"full_name": "Updated Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["email"] == test_user.email
    
    def test_refresh_token(self, client: TestClient, test_db: Session, test_user):
        """Test POST /auth/refresh refreshes access token"""
        # First login to get refresh token
        login_response = client.post(
            "/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        refresh_token = login_data.get("refresh_token")
        
        if refresh_token:
            # Try to refresh
            response = client.post(
                "/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "token_type" in data
    
    def test_logout(self, client: TestClient, auth_headers):
        """Test POST /auth/logout"""
        response = client.post("/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
