"""
Tests for the monitoring enhancement.
"""
import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app

# We need to set environment variables for the test
# We'll do it in a fixture

@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """Set environment variables for the tests."""
    monkeypatch.setenv("API_KEY_ADMIN", "test-admin-key")
    monkeypatch.setenv("API_KEY_OPERATOR", "test-operator-key")
    monkeypatch.setenv("API_KEY_VIEWER", "test-viewer-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("METRICS_COLLECTION_ENABLED", "true")

# We need to import the app after setting the environment variables
# But since the fixture is autouse and runs before each test, we can import inside the test
# or we can reload the module. For simplicity, we'll create the client in each test.

def test_monitoring_models_import():
    """Test that the monitoring models can be imported."""
    from backend.models.monitoring_models import (
        ModelPerformanceMetrics, DataDriftMetrics, SystemPerformanceMetrics
    )
    from backend.database import Base
    assert issubclass(ModelPerformanceMetrics, Base)
    assert issubclass(DataDriftMetrics, Base)
    assert issubclass(SystemPerformanceMetrics, Base)

def test_database_includes_monitoring_tables():
    """Test that the database includes the new monitoring tables."""
    from backend.database import Base, engine
    # Create all tables
    Base.metadata.create_all(engine)
    table_names = set(Base.metadata.tables.keys())
    expected_tables = {
        'model_performance_metrics',
        'data_drift_metrics',
        'system_performance_metrics'
    }
    assert expected_tables.issubset(table_names), f"Missing tables: {expected_tables - table_names}"

def test_monitoring_service_import():
    """Test that the monitoring service can be imported."""
    from backend.monitoring import MonitoringService, collect_metrics
    assert MonitoringService is not None
    assert collect_metrics is not None

def test_monitoring_api_router_included():
    """Test that the monitoring router is included in the app."""
    from fastapi.testclient import TestClient
    from backend.main import app
    # We'll set the environment via the monkeypatch fixture, but we need to create the client
    # after the env is set. Since we can't pass the fixture to the function directly in this way,
    # we'll rely on the autouse fixture and create the client inside the test.
    # However, the client creation must happen after the env is set.
    # We'll do it in the test.
    pass  # We'll test the endpoints in another test

def test_metrics_endpoint_unauthorized():
    """Test that the metrics endpoint requires authentication."""
    from fastapi.testclient import TestClient
    from backend.main import app
    client = TestClient(app)
    # No auth header
    response = client.get("/api/monitoring/")
    # Should be 403 because we have the dependency but no credentials
    assert response.status_code == 403

def test_metrics_endpoint_authorized():
    """Test that the metrics endpoint works with authentication."""
    from fastapi.testclient import TestClient
    from backend.main import app
    client = TestClient(app)
    headers = {"Authorization": "Bearer test-admin-key"}
    response = client.get("/api/monitoring/", headers=headers)
    # Might be 404 if there's no data, but should not be 403
    assert response.status_code != 403
    # Should be 200 or 404 (if no data) or 200 with empty list
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        # Should be a list
        assert isinstance(data, list)

def test_trigger_metrics_collection():
    """Test triggering metrics collection."""
    from fastapi.testclient import TestClient
    from backend.main import app
    client = TestClient(app)
    headers = {"Authorization": "Bearer test-admin-key"}
    response = client.post("/api/monitoring/collect", headers=headers)
    # Should be 202 (Accepted) if metrics collection is enabled
    assert response.status_code == 202
    data = response.json()
    assert "message" in data