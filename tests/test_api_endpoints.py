"""
Tests for API endpoints.
"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# Use a valid API key for testing
VALID_API_KEY = "admin-secret-key-change-in-production"
AUTH_HEADERS = {"Authorization": f"Bearer {VALID_API_KEY}"}

def test_health_endpoint():
    """Test the health endpoint."""
    response = client.get("/health", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI-Based Intelligent Workflow Automation Platform"

def test_create_and_fetch_job():
    """Test creating a job and fetching it."""
    payload = {
        "source": "api",
        "raw_payload": "INVOICE #1001 from Acme Corp for $1200.00"
    }
    response = client.post("/api/jobs", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    job = response.json()
    assert "job_id" in job
    job_id = job["job_id"]
    
    # Fetch the job
    response = client.get(f"/api/jobs/{job_id}", headers=AUTH_HEADERS)
    assert response.status_code == 200
    fetched_job = response.json()
    assert fetched_job["job_id"] == job_id
    assert fetched_job["source"] == "api"
    assert fetched_job["raw_payload"] == "INVOICE #1001 from Acme Corp for $1200.00"

def test_metrics_endpoint():
    """Test the metrics endpoint."""
    response = client.get("/api/metrics", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data
    assert "automation_rate" in data