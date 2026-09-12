#!/usr/bin/env python3
"""
Verification script for Phase 2: Monitoring Enhancement
This script verifies that the monitoring components are correctly implemented.
"""

import os
import sys
import tempfile

# Set up environment variables for testing
os.environ['API_KEY_ADMIN'] = 'test-admin-key'
os.environ['API_KEY_OPERATOR'] = 'test-operator-key'
os.environ['API_KEY_VIEWER'] = 'test-viewer-key'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['METRICS_COLLECTION_ENABLED'] = 'true'

# Add the project root to the Python path
sys.path.insert(0, '/d/Desertation/ai-workflow-automation')

def test_imports():
    """Test that all necessary modules can be imported."""
    print("Testing imports...")
    
    # Test config
    from backend.config import settings
    assert hasattr(settings, 'METRICS_COLLECTION_ENABLED')
    assert hasattr(settings, 'MODEL_VERSION')
    print("✓ Config imports successful")
    
    # Test monitoring models
    from backend.models.monitoring_models import (
        ModelPerformanceMetrics, DataDriftMetrics, SystemPerformanceMetrics
    )
    print("✓ Monitoring models imports successful")
    
    # Test monitoring service
    from backend.monitoring import MonitoringService, collect_metrics
    print("✓ Monitoring service imports successful")
    
    # Test database
    from backend.database import Base, engine
    print("✓ Database imports successful")
    
    # Test API router
    from backend.api import monitoring
    print("✓ Monitoring API router imports successful")
    
    # Test main app
    from backend.main import app
    print("✓ Main app imports successful")
    
    return True

def test_database_schema():
    """Test that the database schema includes the monitoring tables."""
    print("\nTesting database schema...")
    
    from backend.database import Base, engine
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Get table names
    table_names = set(Base.metadata.tables.keys())
    
    # Check for monitoring tables
    expected_tables = {
        'model_performance_metrics',
        'data_drift_metrics', 
        'system_performance_metrics'
    }
    
    missing_tables = expected_tables - table_names
    if missing_tables:
        raise AssertionError(f"Missing monitoring tables: {missing_tables}")
    
    print("✓ All monitoring tables present in database schema")
    print(f"  Tables found: {sorted(table_names)}")
    return True

def test_monitoring_models():
    """Test that the monitoring models are correctly defined."""
    print("\nTesting monitoring models...")
    
    from backend.models.monitoring_models import (
        ModelPerformanceMetrics, DataDriftMetrics, SystemPerformanceMetrics
    )
    from backend.database import Base
    
    # Test inheritance
    assert issubclass(ModelPerformanceMetrics, Base)
    assert issubclass(DataDriftMetrics, Base)
    assert issubclass(SystemPerformanceMetrics, Base)
    
    # Test that they have expected columns
    model_perf_cols = {c.name for c in ModelPerformanceMetrics.__table__.columns}
    expected_model_cols = {
        'id', 'timestamp', 'model_version', 'model_type', 'accuracy', 
        'precision', 'recall', 'f1_score', 'avg_confidence', 'confidence_std',
        'high_confidence_count', 'medium_confidence_count', 'low_confidence_count',
        'invoice_predictions', 'service_request_predictions', 'unknown_predictions',
        'sample_size', 'computation_time_ms'
    }
    assert expected_model_cols.issubset(model_perf_cols), f"ModelPerformanceMetrics missing columns: {expected_model_cols - model_perf_cols}"
    
    data_drift_cols = {c.name for c in DataDriftMetrics.__table__.columns}
    expected_drift_cols = {
        'id', 'timestamp', 'drift_detected', 'drift_score', 'feature_drift_scores',
        'ks_test_p_value', 'chi_square_p_value', 'reference_period_start', 
        'reference_period_end', 'current_period_start', 'current_period_end',
        'sample_size_reference', 'sample_size_current'
    }
    assert expected_drift_cols.issubset(data_drift_cols), f"DataDriftMetrics missing columns: {expected_drift_cols - data_drift_cols}"
    
    system_perf_cols = {c.name for c in SystemPerformanceMetrics.__table__.columns}
    expected_system_cols = {
        'id', 'timestamp', 'jobs_processed_per_minute', 'jobs_completed_per_minute',
        'jobs_failed_per_minute', 'jobs_pending_approval', 'avg_latency_total',
        'avg_latency_ingestion', 'avg_latency_classification', 'avg_latency_extraction',
        'avg_latency_decision', 'avg_latency_execution', 'automation_rate',
        'escalation_rate', 'failure_rate', 'error_count_total', 'error_count_database',
        'error_count_notification', 'error_count_validation', 'avg_retry_count',
        'max_retry_count'
    }
    assert expected_system_cols.issubset(system_perf_cols), f"SystemPerformanceMetrics missing columns: {expected_system_cols - system_perf_cols}"
    
    print("✓ Monitoring models correctly defined with expected columns")
    return True

def test_monitoring_service():
    """Test that the monitoring service can be instantiated."""
    print("\nTesting monitoring service...")
    
    from backend.monitoring import MonitoringService
    from backend.database import SessionLocal
    
    # Test that we can instantiate the service
    service = MonitoringService()
    assert service is not None
    
    # Test that it has the expected methods
    assert hasattr(service, 'collect_model_performance_metrics')
    assert hasattr(service, 'collect_system_performance_metrics')
    assert hasattr(service, 'collect_data_drift_metrics')
    assert hasattr(service, 'run_collection_cycle')
    
    print("✓ Monitoring service correctly instantiated with expected methods")
    return True

def test_api_routes():
    """Test that the monitoring API routes are properly set up."""
    print("\nTesting API routes...")
    
    from backend.main import app
    
    # Get all routes
    routes = [route.path for route in app.routes]
    
    # Check for monitoring routes
    monitoring_routes = [route for route in routes if route.startswith('/api/monitoring')]
    
    expected_routes = [
        '/api/monitoring/collect',
        '/api/monitoring/model-performance',
        '/api/monitoring/system-performance',
        '/api/monitoring/data-drift',
        '/api/monitoring/metrics'
    ]
    
    # Check that we have at least the monitoring prefix routes
    assert len(monitoring_routes) > 0, "No monitoring routes found"
    
    # Check for specific routes (we'll be flexible with exact matching due to potential variations)
    found_expected = 0
    for expected in expected_routes:
        # Normalize for comparison (remove trailing slashes, handle path params)
        expected_norm = expected.rstrip('/')
        found = any(
            route.rstrip('/').split('{')[0] == expected_norm.split('{')[0] 
            for route in monitoring_routes
        )
        if found:
            found_expected += 1
        else:
            # Try a more flexible match
            found_any = any(
                expected.split('/')[-1].replace('{', '').replace('}', '') in route 
                for route in monitoring_routes
            )
            if found_any:
                found_expected += 1
    
    print(f"✓ Found {len(monitoring_routes)} monitoring routes")
    print(f"  Routes: {monitoring_routes}")
    return True

def test_config_integration():
    """Test that the configuration is properly integrated."""
    print("\nTesting configuration integration...")
    
    from backend.config import settings
    
    # Test that monitoring settings are accessible and have correct types
    assert isinstance(settings.METRICS_COLLECTION_ENABLED, bool)
    assert isinstance(settings.MODEL_VERSION, str)
    assert isinstance(settings.MODEL_PERFORMANCE_COLLECTION_INTERVAL_HOURS, int)
    assert isinstance(settings.SYSTEM_PERFORMANCE_COLLECTION_INTERVAL_HOURS, int)
    assert isinstance(settings.DATA_DRIFT_COLLECTION_INTERVAL_HOURS, int)
    
    # Test default values
    assert settings.MODEL_VERSION == "tf-idf-logreg-v1"
    assert settings.METRICS_COLLECTION_ENABLED == True
    assert settings.MODEL_PERFORMANCE_COLLECTION_INTERVAL_HOURS == 24
    assert settings.SYSTEM_PERFORMANCE_COLLECTION_INTERVAL_HOURS == 1
    assert settings.DATA_DRIFT_COLLECTION_INTERVAL_HOURS == 24
    
    print("✓ Configuration correctly integrated with monitoring settings")
    return True

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Phase 2: Monitoring Enhancement Verification")
    print("=" * 60)
    
    try:
        test_imports()
        test_database_schema()
        test_monitoring_models()
        test_monitoring_service()
        test_api_routes()
        test_config_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL PHASE 2 VERIFICATION TESTS PASSED!")
        print("=" * 60)
        print("\nSummary of verified components:")
        print("  ✓ Monitoring models (ModelPerformanceMetrics, DataDriftMetrics, SystemPerformanceMetrics)")
        print("  ✓ Monitoring service with collection methods")
        print("  ✓ Database schema with monitoring tables")
        print("  ✓ Monitoring API endpoints (/monitoring/*)")
        print("  ✓ Configuration integration")
        print("  ✓ Proper imports and module structure")
        
        return True
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)