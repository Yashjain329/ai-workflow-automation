from fastapi.testclient import TestClient
from backend.main import app
from backend.connectors.database_connector import DatabaseConnector

client = TestClient(app)

def test_malformed_empty_payload():
    DatabaseConnector.set_failure_mode("NORMAL")
    payload = {"source": "api", "raw_payload": ""}
    res = client.post("/api/jobs", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["APPROVAL_PENDING", "FAILED", "AUDITED"]

def test_high_amount_escalation_scenario():
    DatabaseConnector.set_failure_mode("NORMAL")
    # Invoice over $5000 should escalate to human queue
    payload = {
        "source": "api",
        "raw_payload": "Statement of account issued by TechCorp for reference INV-2026-9900 totaling $15000.00."
    }
    res = client.post("/api/jobs", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "APPROVAL_PENDING"
    assert data["human_intervention"] == True

    # Verify task in approval queue
    res_approvals = client.get("/api/approvals")
    tasks = res_approvals.json()
    matching_tasks = [t for t in tasks if t["job_id"] == data["job_id"]]
    assert len(matching_tasks) == 1
    task_id = matching_tasks[0]["task_id"]

    # Approve task
    res_dec = client.post(f"/api/approvals/{task_id}/decision", json={"decision": "APPROVED", "reviewer": "test_admin"})
    assert res_dec.status_code == 200
    assert res_dec.json()["status"] == "AUDITED"
