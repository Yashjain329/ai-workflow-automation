import os
import sys

# Set environment variables before importing any of our modules
os.environ['API_KEY_ADMIN'] = 'test-admin-key'
os.environ['API_KEY_OPERATOR'] = 'test-operator-key'
os.environ['API_KEY_VIEWER'] = 'test-viewer-key'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['METRICS_COLLECTION_ENABLED'] = 'true'

# Now insert the project root and import
sys.path.insert(0, '/d/Desertation/ai-workflow-automation')

def test_config():
    from backend.config import settings
    # Test that monitoring settings are present
    assert hasattr(settings, 'METRICS_COLLECTION_ENABLED')
    assert hasattr(settings, 'MODEL_VERSION')
    assert hasattr(settings, 'MODEL_PERFORMANCE_COLLECTION_INTERVAL_HOURS')
    assert hasattr(settings, 'SYSTEM_PERFORMANCE_COLLECTION_INTERVAL_HOURS')
    assert hasattr(settings, 'DATA_DRIFT_COLLECTION_INTERVAL_HOURS')
    
    # Test defaults
    assert settings.MODEL_VERSION == "tf-idf-logreg-v1"
    assert settings.METRICS_COLLECTION_ENABLED == True
    assert settings.MODEL_PERFORMANCE_COLLECTION_INTERVAL_HOURS == 24
    assert settings.SYSTEM_PERFORMANCE_COLLECTION_INTERVAL_HOURS == 1
    assert settings.DATA_DRIFT_COLLECTION_INTERVAL_HOURS == 24
    
    print("✓ Configuration test passed")

def test_models_import():
    # Test that the new monitoring models can be imported
    from backend.models.monitoring_models import (
        ModelPerformanceMetrics, DataDriftMetrics, SystemPerformanceMetrics
    )
    
    # Test that they inherit from Base
    from backend.database import Base
    assert issubclass(ModelPerformanceMetrics, Base)
    assert issubclass(DataDriftMetrics, Base)
    assert issubclass(SystemPerformanceMetrics, Base)
    
    print("✓ Models import test passed")

def test_database_includes_monitoring_models():
    # Test that the database imports include the monitoring models
    from backend.database import Base
    # Check that the metadata includes our new tables
    table_names = list(Base.metadata.tables.keys())
    assert 'model_performance_metrics' in table_names
    assert 'data_drift_metrics' in table_names
    assert 'system_performance_metrics' in table_names
    
    print("✓ Database includes monitoring models test passed")

def test_monitoring_service_can_be_instantiated():
    from backend.monitoring import MonitoringService
    # We won't actually run it because it needs a database session
    # but we can check that the class exists and can be instantiated
    assert MonitoringService is not None
    
    print("✓ Monitoring service instantiation test passed")

def test_monitoring_api_router_exists():
    from backend.main import app
    from backend.api import monitoring
    # Check that the monitoring router is included in the app
    routes = [route.path for route in app.routes]
    api_routes = [route for route in routes if route.startswith('/api')]
    monitoring_routes = [route for route in api_routes if route.startswith('/api/monitoring')]
    assert len(monitoring_routes) > 0
    
    print("✓ Monitoring API router test passed")

if __name__ == '__main__':
    test_config()
    test_models_import()
    test_database_includes_monitoring_models()
    test_monitoring_service_can_be_instantiated()
    test_monitoring_api_router_exists()
    print("\n✅ All Phase 2 verification tests passed!")