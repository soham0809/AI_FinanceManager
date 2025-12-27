"""
Test Transaction Endpoints
Comprehensive tests for transaction CRUD, SMS parsing, search
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.transactions
class TestTransactionRoutes:
    """Test transaction endpoints"""
    
    def test_parse_sms_authenticated(self, client: TestClient, auth_headers, sample_sms_messages):
        """Test POST /v1/parse-sms-local with authentication"""
        response = client.post(
            "/v1/parse-sms-local",
            headers=auth_headers,
            json={"sms_text": sample_sms_messages[0]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "vendor" in data
        assert "amount" in data
        assert "category" in data
        assert "confidence" in data
        assert data["amount"] > 0
    
    def test_parse_sms_unauthorized(self, client: TestClient, sample_sms_messages):
        """Test SMS parsing without authentication fails"""
        response = client.post(
            "/v1/parse-sms-local",
            json={"sms_text": sample_sms_messages[0]}
        )
        
        assert response.status_code == 401
    
    def test_get_transactions(self, client: TestClient, auth_headers, sample_transactions):
        """Test GET /v1/transactions returns user's transactions"""
        response = client.get("/v1/transactions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert len(data) == len(sample_transactions)
    
    def test_get_transactions_pagination(self, client: TestClient, auth_headers, sample_transactions):
        """Test GET /v1/transactions with pagination"""
        response = client.get(
            "/v1/transactions?limit=3&offset=0",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3
    
    def test_get_transactions_unauthorized(self, client: TestClient):
        """Test getting transactions without authentication"""
        response = client.get("/v1/transactions")
        
        assert response.status_code == 401
    
    def test_get_transactions_user_isolation(self, client: TestClient, test_db: Session, 
                                             auth_headers, sample_transactions, another_user):
        """Test users only see their own transactions"""
        # Get token for another user
        from app.controllers.auth_controller import AuthController
        token_data = AuthController.create_access_token_for_user(another_user, test_db)
        another_headers = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "Content-Type": "application/json"
        }
        
        response = client.get("/v1/transactions", headers=another_headers)
        
        assert response.status_code == 200
        data = response.json()
        # Another user should have no transactions
        assert len(data) == 0
    
    def test_get_transaction_by_id(self, client: TestClient, auth_headers, sample_transactions):
        """Test GET /v1/transactions/{id}"""
        transaction_id = sample_transactions[0].id
        
        response = client.get(
            f"/v1/transactions/{transaction_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction_id
        assert "vendor" in data
        assert "amount" in data
    
    def test_get_transaction_not_found(self, client: TestClient, auth_headers):
        """Test getting non-existent transaction"""
        response = client.get(
            "/v1/transactions/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_create_transaction(self, client: TestClient, auth_headers):
        """Test POST /v1/transactions creates transaction manually"""
        from datetime import datetime
        
        response = client.post(
            "/v1/transactions",
            headers=auth_headers,
            json={
                "vendor": "Manual Vendor",
                "amount": 1000.0,
                "date": datetime.now().isoformat(),
                "category": "Shopping",
                "confidence": 1.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["vendor"] == "Manual Vendor"
        assert data["amount"] == 1000.0
        assert data["category"] == "Shopping"
    
    def test_update_transaction(self, client: TestClient, auth_headers, sample_transactions):
        """Test PUT /v1/transactions/{id}"""
        transaction_id = sample_transactions[0].id
        
        response = client.put(
            f"/v1/transactions/{transaction_id}",
            headers=auth_headers,
            json={"category": "Updated Category"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "Updated Category"
    
    def test_update_transaction_not_owned(self, client: TestClient, test_db: Session,
                                          sample_transactions, another_user):
        """Test updating another user's transaction fails"""
        from app.controllers.auth_controller import AuthController
        token_data = AuthController.create_access_token_for_user(another_user, test_db)
        another_headers = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "Content-Type": "application/json"
        }
        
        transaction_id = sample_transactions[0].id
        
        response = client.put(
            f"/v1/transactions/{transaction_id}",
            headers=another_headers,
            json={"category": "Hacked Category"}
        )
        
        assert response.status_code in [403, 404]
    
    def test_delete_transaction(self, client: TestClient, auth_headers, sample_transactions):
        """Test DELETE /v1/transactions/{id}"""
        transaction_id = sample_transactions[0].id
        
        response = client.delete(
            f"/v1/transactions/{transaction_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify deleted
        get_response = client.get(
            f"/v1/transactions/{transaction_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    def test_search_transactions(self, client: TestClient, auth_headers, sample_transactions):
        """Test GET /v1/search"""
        response = client.get(
            "/v1/search?q=Amazon",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should find Amazon transaction
        assert any("Amazon" in tx["vendor"] for tx in data)
    
    def test_ml_info(self, client: TestClient):
        """Test GET /v1/ml-info returns model information"""
        response = client.get("/v1/ml-info")
        
        assert response.status_code == 200
        data = response.json()
        assert "model_name" in data
        assert "categories" in data
        assert "capabilities" in data
        assert isinstance(data["categories"], list)
