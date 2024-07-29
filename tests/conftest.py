import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import pytest

# Add the path to the project's root directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pymasters.database.models import Base, User
from pymasters.database.db import get_db
from pymasters.repository.auth import Hash

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a sessionmaker for the test database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database session
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Fixture for setting up the test database
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create tables before starting the tests
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after completing the tests
    Base.metadata.drop_all(bind=engine)

# Fixture to provide a test session
@pytest.fixture(scope="function")
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fixture to create a test user
@pytest.fixture(scope="function")
def test_user(test_db):
    # Clear the users table before creating a new user
    test_db.query(User).delete()
    test_db.commit()

    hashed_password = Hash().get_password_hash("testpassword")
    user = User(email="test@example.com", password=hashed_password)
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

# Fixture for the FastAPI client
@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from pymasters.main import app  # Import the FastAPI app

    # Override the get_db dependency with the test session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c




























