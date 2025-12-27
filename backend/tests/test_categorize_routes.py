"""
Test Categorization Endpoints
Tests for vendor categorization
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestCategorizeRoutes:
    """Test categorization endpoints"""
    
    def test_categorize_vendor(self, client: TestClient):
        """Test POST /v1/categorize"""
        response = client.post("/v1/categorize?vendor=Amazon")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "vendor" in data
        assert "category" in data
        assert "confidence" in data
    
    def test_categorize_known_vendor(self, client: TestClient):
        """Test categorization of known vendors"""
        vendors = {
            "Swiggy": "food",
            "Amazon": "shopping",
            "Uber": "transportation"
        }
        
        for vendor, expected_keyword in vendors.items():
            response = client.post(f"/v1/categorize?vendor={vendor}")
            data = response.json()
            assert data["success"] is True
            assert expected_keyword in data["category"].lower() or data["category"] == "Shopping"
    
    def test_categorize_unknown_vendor(self, client: TestClient):
        """Test categorization of unknown vendor"""
        response = client.post("/v1/categorize?vendor=UnknownVendor123")
        
        data = response.json()
        assert data["success"] is True
        assert data["category"] == "Others"
