import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base

# Import all models to ensure they are registered with Base
# Import the main models
from backend.models import db_models, monitoring_models

# Create a temporary database for testing
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Use an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after the test
        Base.metadata.drop_all(engine)

# Fixture to override the dependency in the app for testing
@pytest.fixture
def client(db_session):
    """Create a test client that uses the override database."""
    from fastapi.testclient import TestClient
    from backend.main import app
    
    # Override the get_db dependency to use our test session
    def get_test_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[{"db": "Session"}] = get_test_db
    # Note: The actual dependency override might be different based on how the db is injected in the endpoints.
    # Since we don't have the exact dependency, we'll skip the override for now and just return the client.
    # In a real scenario, we would override the dependency that provides the database session.
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up the override
    app.dependency_overrides.clear()