"""
Test Health Check Endpoints
Tests for root and health check endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthRoutes:
    """Test health check and root endpoints"""
    
    @pytest.mark.unit
    def test_root_endpoint(self, client: TestClient):
        """Test GET / returns welcome message"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "healthy"
    
    @pytest.mark.unit
    def test_health_check(self, client: TestClient):
        """Test GET /health returns health status"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
        assert "app" in data
        assert "version" in data
    
    @pytest.mark.unit
    def test_health_check_response_structure(self, client: TestClient):
        """Test health check response has correct structure"""
        response = client.get("/health")
        data = response.json()
        
        # Verify all required fields
        required_fields = ["status", "message", "app", "version"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
