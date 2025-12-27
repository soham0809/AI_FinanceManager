"""
Test Chatbot Endpoints
Tests for chatbot query, summary, and insights
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.chatbot
@pytest.mark.slow
class TestChatbotRoutes:
    """Test chatbot endpoints"""
    
    def test_chatbot_query(self, client: TestClient, sample_transactions):
        """Test POST /v1/chatbot/query"""
        response = client.post(
            "/v1/chatbot/query",
            json={
                "query": "How much did I spend this month?",
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "transaction_count" in data
        assert "query" in data
    
    def test_chatbot_query_no_transactions(self, client: TestClient):
        """Test chatbot with no transactions"""
        response = client.post(
            "/v1/chatbot/query",
            json={
                "query": "Show my spending",
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_count"] == 0
        assert "no transactions" in data["response"].lower()
    
    def test_chatbot_summary(self, client: TestClient, sample_transactions):
        """Test GET /v1/chatbot/summary"""
        response = client.get("/v1/chatbot/summary?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data or "status" in data
    
    def test_quick_insights(self, client: TestClient, sample_transactions):
        """Test POST /v1/chatbot/quick-insights"""
        response = client.post("/v1/chatbot/quick-insights")
        
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
        assert "transaction_count" in data
    
    def test_quick_insights_no_data(self, client: TestClient):
        """Test quick insights with no transactions"""
        response = client.post("/v1/chatbot/quick-insights")
        
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_count"] == 0
