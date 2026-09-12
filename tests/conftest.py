import os
import sys
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """Set environment variables for the tests."""
    monkeypatch.setenv("API_KEY_ADMIN", "test-admin-key")
    monkeypatch.setenv("API_KEY_OPERATOR", "test-operator-key")
    monkeypatch.setenv("API_KEY_VIEWER", "test-viewer-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("METRICS_COLLECTION_ENABLED", "true")

@pytest.fixture
def client():
    # Remove backend modules from sys.modules so they are reloaded with the new environment variables
    module_names = list(sys.modules.keys())
    for module_name in module_names:
        if module_name.startswith('backend.'):
            del sys.modules[module_name]
    
    # Now import the backend modules
    from backend.database import Base, engine
    from backend.main import app
    from backend.database import get_db
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Override the get_db dependency
    def get_test_db():
        try:
            db = SessionLocal()
            yield db
        finally:
            db.close()
    
    # We need to import SessionLocal from backend.database
    from backend.database import SessionLocal
    
    app.dependency_overrides[get_db] = get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()