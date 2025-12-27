"""
Test Monthly Analytics Endpoints
Tests for monthly summary and yearly overview
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime


@pytest.mark.analytics
class TestMonthlyRoutes:
    """Test monthly analytics endpoints"""
    
    def test_monthly_summary_current(self, client: TestClient, auth_headers, sample_transactions):
        """Test GET /v1/analytics/monthly/summary for current month"""
        response = client.get("/v1/analytics/monthly/summary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
    
    def test_monthly_summary_specific_month(self, client: TestClient, auth_headers, sample_transactions):
        """Test monthly summary for specific month"""
        now = datetime.now()
        response = client.get(
            f"/v1/analytics/monthly/summary?year={now.year}&month={now.month}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_monthly_summary_structure(self, client: TestClient, auth_headers, sample_transactions):
        """Test monthly summary response structure"""
        response = client.get("/v1/analytics/monthly/summary", headers=auth_headers)
        data = response.json()
        
        if data.get("success"):
            assert "data" in data
            if data["data"]:
                assert "month" in data["data"] or "total_spent" in data["data"]
    
    def test_yearly_overview(self, client: TestClient, auth_headers, sample_transactions):
        """Test GET /v1/analytics/monthly/yearly-overview"""
        response = client.get("/v1/analytics/monthly/yearly-overview", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
    
    def test_yearly_overview_specific_year(self, client: TestClient, auth_headers, sample_transactions):
        """Test yearly overview for specific year"""
        year = datetime.now().year
        response = client.get(
            f"/v1/analytics/monthly/yearly-overview?year={year}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
    
    def test_yearly_overview_structure(self, client: TestClient, auth_headers, sample_transactions):
        """Test yearly overview response structure"""
        response = client.get("/v1/analytics/monthly/yearly-overview", headers=auth_headers)
        data = response.json()
        
        if data.get("success") and data.get("data"):
            assert "year" in data["data"] or "months" in data["data"] or "summary" in data["data"]
    
    def test_monthly_unauthorized(self, client: TestClient):
        """Test monthly endpoints require authentication"""
        endpoints = [
            "/v1/analytics/monthly/summary",
            "/v1/analytics/monthly/yearly-overview"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
