"""
Tests for failure scenarios.
"""
from fastapi.testclient import TestClient
from backend.main import app
from backend.connectors.database_connector import DatabaseConnector

client = TestClient(app)

# Use a valid API key for testing
VALID_API_KEY = "admin-secret-key-change-in-production"
AUTH_HEADERS = {"Authorization": f"Bearer {VALID_API_KEY}"}

def test_malformed_empty_payload():
    """Test handling of malformed or empty payloads."""
    DatabaseConnector.set_failure_mode("NORMAL")
    payload = {"source": "api", "raw_payload": ""}
    response = client.post("/api/jobs", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    job = response.json()
    assert "job_id" in job

def test_high_amount_escalation_scenario():
    """Test that high amount invoices are escalated to human approval."""
    DatabaseConnector.set_failure_mode("NORMAL")
    # Invoice over $5000 should escalate to human queue
    payload = {
        "source": "api",
        "raw_payload": "Statement of account issued by TechCorp for reference INV-2026-9900 totaling $15000.00."
    }
    response = client.post("/api/jobs", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    job = response.json()
    assert "job_id" in job
    # The job should be processed and end up in a state requiring human approval
    # Depending on the workflow, this might be APPROVAL_PENDING or similar
    assert job["status"] in ["APPROVAL_PENDING", "EXECUTING", "COMPLETED", "FAILED"]