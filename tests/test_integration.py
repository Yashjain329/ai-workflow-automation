"""
Integration tests for the workflow system.
"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# Use a valid API key for testing
VALID_API_KEY = "admin-secret-key-change-in-production"
AUTH_HEADERS = {"Authorization": f"Bearer {VALID_API_KEY}"}

def test_health_endpoint_integration():
    """Test that the health endpoint works."""
    response = client.get("/health", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI-Based Intelligent Workflow Automation Platform"

def test_create_and_retrieve_job_integration():
    """Test creating a job and retrieving it."""
    # First, create a job
    job_data = {
        "source": "api",
        "raw_payload": "INVOICE #12345 FROM ACME CORP FOR $1500.00"
    }
    response = client.post("/api/jobs/", json=job_data, headers=AUTH_HEADERS)
    assert response.status_code == 200
    job = response.json()
    assert "job_id" in job
    job_id = job["job_id"]
    
    # Then retrieve the job
    response = client.get(f"/api/jobs/{job_id}", headers=AUTH_HEADERS)
    assert response.status_code == 200
    retrieved_job = response.json()
    assert retrieved_job["job_id"] == job_id
    assert retrieved_job["source"] == "api"
    assert retrieved_job["raw_payload"] == "INVOICE #12345 FROM ACME CORP FOR $1500.00"
    # The job should have been processed through the workflow
    assert retrieved_job["status"] in ["RECEIVED", "VALIDATING", "CLASSIFIED", "EXTRACTED", "DECIDING", 
                                     "APPROVAL_PENDING", "EXECUTING", "COMPLETED", "FAILED", "AUDITED"]

def test_metrics_endpoint_integration():
    """Test that the metrics endpoint works."""
    response = client.get("/api/metrics/", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    # Should return a dict with metrics
    assert isinstance(data, dict)