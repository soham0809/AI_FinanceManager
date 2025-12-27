"""
Test Enhanced Chatbot Endpoints
Tests for enhanced chatbot with caching and context
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.chatbot
@pytest.mark.slow
class TestEnhancedChatbotRoutes:
    """Test enhanced chatbot endpoints"""
    
    def test_enhanced_ask(self, client: TestClient, auth_headers, sample_transactions):
        """Test POST /v1/enhanced-chatbot/ask"""
        response = client.post(
            "/v1/enhanced-chatbot/ask",
            headers=auth_headers,
            json={
                "query": "What are my top spending categories?",
                "use_cache": True,
                "include_context": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "transaction_count" in data
        assert "cached" in data
        assert "processing_time" in data
        assert "context_used" in data
        assert "data_quality" in data
    
    def test_enhanced_ask_no_cache(self, client: TestClient, auth_headers, sample_transactions):
        """Test enhanced chatbot without cache"""
        response = client.post(
            "/v1/enhanced-chatbot/ask",
            headers=auth_headers,
            json={
                "query": "How much did I spend?",
                "use_cache": False,
                "include_context": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is False
    
    def test_enhanced_ask_no_context(self, client: TestClient, auth_headers, sample_transactions):
        """Test enhanced chatbot without context"""
        response = client.post(
            "/v1/enhanced-chatbot/ask",
            headers=auth_headers,
            json={
                "query": "Tell me about my spending",
                "include_context": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "context_used" in data
    
    def test_enhanced_ask_refresh_session(self, client: TestClient, auth_headers, sample_transactions):
        """Test session refresh"""
        response = client.post(
            "/v1/enhanced-chatbot/ask",
            headers=auth_headers,
            json={
                "query": "Monthly spending summary",
                "refresh_session": True
            }
        )
        
        assert response.status_code == 200
    
    def test_enhanced_ask_no_data(self, client: TestClient, auth_headers):
        """Test enhanced chatbot with no transactions"""
        response = client.post(
            "/v1/enhanced-chatbot/ask",
            headers=auth_headers,
            json={"query": "Show my transactions"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_count"] == 0
    
    def test_data_quality_report(self, client: TestClient, auth_headers, sample_transactions):
        """Test GET /v1/enhanced-chatbot/data-quality"""
        response = client.get("/v1/enhanced-chatbot/data-quality", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data_quality" in data
        assert "recommendations" in data
    
    def test_data_quality_structure(self, client: TestClient, auth_headers, sample_transactions):
        """Test data quality report structure"""
        response = client.get("/v1/enhanced-chatbot/data-quality", headers=auth_headers)
        data = response.json()
        
        if data.get("success"):
            quality = data["data_quality"]
            assert "total_transactions" in quality or "quality_score" in quality or "status" in quality
    
    def test_save_conversation(self, client: TestClient, auth_headers):
        """Test POST /v1/enhanced-chatbot/conversation-history"""
        response = client.post(
            "/v1/enhanced-chatbot/conversation-history",
            headers=auth_headers,
            params={
                "query": "test query",
                "response": "test response"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
    
    def test_enhanced_chatbot_unauthorized(self, client: TestClient):
        """Test enhanced chatbot requires authentication"""
        response = client.post(
            "/v1/enhanced-chatbot/ask",
            json={"query": "test"}
        )
        
        assert response.status_code == 401
