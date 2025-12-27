"""
Test Analytics Endpoints
Tests for financial insights, spending analysis, trends
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.analytics
class TestAnalyticsRoutes:
    """Test analytics endpoints"""
    
    def test_get_insights(self, client: TestClient, auth_headers, sample_transactions):
        """Test GET /v1/analytics/insights"""
        response = client.get("/v1/analytics/insights", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_transactions" in data
        assert "total_spending" in data
        assert "total_income" in data
        assert "insights" in data
        assert data["total_transactions"] > 0
    
    def test_get_insights_no_data(self, client: TestClient, auth_headers):
        """Test insights with no transactions"""
        response = client.get("/v1/analytics/insights", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_transactions"] == 0
    
    def test_get_insights_unauthorized(self, client: TestClient):
        """Test insights without authentication"""
        response = client.get("/v1/analytics/insights")
        
        assert response.status_code == 401
    
    def test_spending_by_category(self, client: TestClient, auth_headers, sample_transactions):
        """Test GET /v1/analytics/spending-by-category"""
        response = client.get("/v1/analytics/spending-by-category", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "categories" in data
        assert "total_spending" in data
        assert "analysis" in data
        assert isinstance(data["categories"], dict)
    
    def test_spending_by_category_structure(self, client: TestClient, auth_headers, sample_transactions):
        """Test category spending has correct structure"""
        response = client.get("/v1/analytics/spending-by-category", headers=auth_headers)
        data = response.json()
        
        if data["categories"]:
            first_category = next(iter(data["categories"].values()))
            assert "total_amount" in first_category
            assert "transaction_count" in first_category
            assert "avg_amount" in first_category
    
    def test_monthly_trends(self, client: TestClient, auth_headers, sample_transactions):
        """Test GET /v1/analytics/monthly-trends"""
        response = client.get("/v1/analytics/monthly-trends", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "monthly_trends" in data
        assert "trend_analysis" in data
    
    def test_monthly_trends_format(self, client: TestClient, auth_headers, sample_transactions):
        """Test monthly trends data format"""
        response = client.get("/v1/analytics/monthly-trends", headers=auth_headers)
        data = response.json()
        
        if data["monthly_trends"]:
            # Check month key format (YYYY-MM)
            for month_key in data["monthly_trends"].keys():
                assert len(month_key.split("-")) == 2
    
    def test_top_vendors(self, client: TestClient, auth_headers, sample_transactions):
        """Test GET /v1/analytics/top-vendors"""
        response = client.get("/v1/analytics/top-vendors", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "top_vendors" in data
        assert isinstance(data["top_vendors"], list)
    
    def test_top_vendors_limit(self, client: TestClient, auth_headers, sample_transactions):
        """Test top vendors with limit parameter"""
        response = client.get("/v1/analytics/top-vendors?limit=3", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["top_vendors"]) <= 3
    
    def test_top_vendors_structure(self, client: TestClient, auth_headers, sample_transactions):
        """Test vendor data structure"""
        response = client.get("/v1/analytics/top-vendors", headers=auth_headers)
        data = response.json()
        
        if data["top_vendors"]:
            vendor = data["top_vendors"][0]
            assert "vendor" in vendor
            assert "total_spending" in vendor
            assert "transaction_count" in vendor
            assert "avg_spending" in vendor
    
    def test_analytics_user_isolation(self, client: TestClient, test_db, 
                                     sample_transactions, another_user):
        """Test analytics only show user's own data"""
        from app.controllers.auth_controller import AuthController
        token_data = AuthController.create_access_token_for_user(another_user, test_db)
        another_headers = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "Content-Type": "application/json"
        }
        
        response = client.get("/v1/analytics/insights", headers=another_headers)
        
        assert response.status_code == 200
        data = response.json()
        # Another user has no transactions
        assert data["total_transactions"] == 0
