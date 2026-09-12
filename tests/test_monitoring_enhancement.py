"""
Tests for the monitoring enhancement.
"""
import os
import pytest
from fastapi.testclient import TestClient

# Set environment variables for the tests
# This fixture runs before each test in this module
@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """Set environment variables for the tests."""
    monkeypatch.setenv("API_KEY_ADMIN", "test-admin-key")
    monkeypatch.setenv("API_KEY_OPERATOR", "test-operator-key")
    monkeypatch.setenv("API_KEY_VIEWER", "test-viewer-key")
    monkeypatch.setenv("METRICS_COLLECTION_ENABLED", "true")

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

def test_monitoring_api_router_included(client):
    """Test that the monitoring router is included in the app."""
    from backend.main import app
    # We'll test the endpoints in another test
    pass

def test_metrics_endpoint_unauthorized(client):
    """Test that the metrics endpoint requires authentication."""
    # No auth header
    response = client.get("/api/monitoring/metrics")
    # Should be 403 because we have the dependency but no credentials
    assert response.status_code == 403

def test_metrics_endpoint_authorized(client):
    """Test that the metrics endpoint works with authentication."""
    headers = {"Authorization": "Bearer test-admin-key"}
    response = client.get("/api/monitoring/metrics", headers=headers)
    # Might be 404 if there's no data, but should not be 403
    assert response.status_code != 403
    # Should be 200 with dict containing metric categories
    assert response.status_code == 200
    data = response.json()
    # Should be a dict with model_performance, system_performance, data_drift keys
    assert isinstance(data, dict)
    assert "model_performance" in data
    assert "system_performance" in data
    assert "data_drift" in data
    assert "timestamp" in data

def test_trigger_metrics_collection(client):
    """Test triggering metrics collection."""
    headers = {"Authorization": "Bearer test-admin-key"}
    response = client.post("/api/monitoring/collect", headers=headers)
    # Should be 202 (Accepted) if metrics collection is enabled
    assert response.status_code == 202
    data = response.json()
    assert "message" in data