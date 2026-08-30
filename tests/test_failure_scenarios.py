from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_malformed_empty_payload():
    payload = {"source": "api", "raw_payload": ""}
    res = client.post("/api/jobs", json=payload)
    assert res.status_code == 200
    data = res.json()
    # Empty payloads have unknown category & high policy risk -> safely routed to approval queue or audited
    assert data["status"] in ["APPROVAL_PENDING", "FAILED", "AUDITED"]

def test_high_amount_escalation_scenario():
    # Invoice over $5000 should escalate to human queue
    payload = {
        "source": "api",
        "raw_payload": "INVOICE #9900 from TechCorp for $15000.00"
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
