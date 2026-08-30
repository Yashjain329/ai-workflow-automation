from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_create_and_fetch_job():
    payload = {
        "source": "api",
        "raw_payload": "INVOICE #1001 from Acme Corp for $1200.00"
    }
    res = client.post("/api/jobs", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "job_id" in data
    assert data["category"] == "invoice"

    job_id = data["job_id"]
    res_detail = client.get(f"/api/jobs/{job_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["job"]["job_id"] == job_id
    assert detail["prediction"]["predicted_category"] == "invoice"

def test_metrics_endpoint():
    res = client.get("/api/metrics")
    assert res.status_code == 200
    metrics = res.json()
    assert "total_jobs" in metrics
    assert "automation_rate" in metrics
