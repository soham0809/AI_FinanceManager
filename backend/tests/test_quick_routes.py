"""
Test Quick/Async Routes
Tests for background job processing and batch operations
"""
import pytest
import time
from fastapi.testclient import TestClient


@pytest.mark.slow
class TestQuickRoutes:
    """Test quick/async processing endpoints"""
    
    def test_quick_parse_sms(self, client: TestClient, auth_headers, sample_sms_messages):
        """Test POST /v1/quick/parse-sms"""
        response = client.post(
            "/v1/quick/parse-sms",
            headers=auth_headers,
            json={"sms_text": sample_sms_messages[0]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "status" in data
        assert data["status"] == "processing"
    
    def test_quick_parse_sms_local(self, client: TestClient, auth_headers, sample_sms_messages):
        """Test POST /v1/quick/parse-sms-local"""
        response = client.post(
            "/v1/quick/parse-sms-local",
            headers=auth_headers,
            json={"sms_text": sample_sms_messages[0]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "status" in data
    
    def test_parse_sms_batch(self, client: TestClient, auth_headers, sample_sms_messages):
        """Test POST /v1/quick/parse-sms-batch"""
        response = client.post(
            "/v1/quick/parse-sms-batch",
            headers=auth_headers,
            json={
                "sms_texts": sample_sms_messages[:3],
                "batch_size": 2,
                "delay_seconds": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "total" in data
        assert data["total"] == 3
    
    def test_parse_sms_batch_local(self, client: TestClient, auth_headers, sample_sms_messages):
        """Test POST /v1/quick/parse-sms-batch-local"""
        response = client.post(
            "/v1/quick/parse-sms-batch-local",
            headers=auth_headers,
            json={
                "sms_texts": sample_sms_messages[:2],
                "batch_size": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["total"] == 2
    
    def test_job_status(self, client: TestClient, auth_headers, sample_sms_messages):
        """Test GET /v1/quick/job-status/{job_id}"""
        # Create a job first
        create_response = client.post(
            "/v1/quick/parse-sms-local",
            headers=auth_headers,
            json={"sms_text": sample_sms_messages[0]}
        )
        job_id = create_response.json()["job_id"]
        
        # Check status
        response = client.get(f"/v1/quick/job-status/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert "status" in data
    
    def test_job_status_not_found(self, client: TestClient):
        """Test job status with invalid job ID"""
        response = client.get("/v1/quick/job-status/invalid-job-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_found"
    
    def test_cleanup_job(self, client: TestClient, auth_headers, sample_sms_messages):
        """Test DELETE /v1/quick/job/{job_id}"""
        # Create a job
        create_response = client.post(
            "/v1/quick/parse-sms-local",
            headers=auth_headers,
            json={"sms_text": sample_sms_messages[0]}
        )
        job_id = create_response.json()["job_id"]
        
        # Cleanup
        response = client.delete(f"/v1/quick/job/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_quick_routes_unauthorized(self, client: TestClient, sample_sms_messages):
        """Test quick routes require authentication"""
        response = client.post(
            "/v1/quick/parse-sms",
            json={"sms_text": sample_sms_messages[0]}
        )
        
        assert response.status_code == 401
