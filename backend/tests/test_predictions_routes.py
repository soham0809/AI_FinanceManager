"""
Test Predictions Endpoints
Tests for savings goals and model training
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestPredictionsRoutes:
    """Test predictions endpoints"""
    
    def test_create_savings_goal(self, client: TestClient):
        """Test POST /v1/predictions/savings-goal"""
        response = client.post(
            "/v1/predictions/savings-goal",
            json={
                "target_amount": 100000.0,
                "target_months": 12,
                "current_income": 50000.0,
                "current_expenses": 30000.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "goal_id" in data
        assert "target_amount" in data
        assert "monthly_required" in data
        assert "achievable" in data
        assert "recommendation" in data
        assert data["target_amount"] == 100000.0
    
    def test_savings_goal_achievable(self, client: TestClient):
        """Test achievable savings goal calculation"""
        response = client.post(
            "/v1/predictions/savings-goal",
            json={
                "target_amount": 10000.0,
                "target_months": 12,
                "current_income": 50000.0,
                "current_expenses": 30000.0
            }
        )
        
        data = response.json()
        # With 20000 surplus per month, 10000 in 12 months is achievable
        assert data["achievable"] is True
    
    def test_savings_goal_validation_negative_amount(self, client: TestClient):
        """Test savings goal with invalid negative amount"""
        response = client.post(
            "/v1/predictions/savings-goal",
            json={
                "target_amount": -1000.0,
                "target_months": 12,
                "current_income": 50000.0,
                "current_expenses": 30000.0
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_savings_goal_validation_zero_months(self, client: TestClient):
        """Test savings goal with zero months"""
        response = client.post(
            "/v1/predictions/savings-goal",
            json={
                "target_amount": 10000.0,
                "target_months": 0,
                "current_income": 50000.0,
                "current_expenses": 30000.0
            }
        )
        
        assert response.status_code == 422
    
    def test_train_models(self, client: TestClient, test_db, sample_transactions):
        """Test POST /v1/predictions/train-models"""
        response = client.post("/v1/predictions/train-models")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories_trained" in data
        assert "message" in data
        assert isinstance(data["categories_trained"], list)
    
    def test_train_models_no_data(self, client: TestClient, test_db):
        """Test model training with no transactions"""
        response = client.post("/v1/predictions/train-models")
        
        # Should still succeed, just with empty categories
        assert response.status_code == 200
        data = response.json()
        assert "categories_trained" in data
