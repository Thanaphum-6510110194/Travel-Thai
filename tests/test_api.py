import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine) # ล้างข้อมูลเก่า
    Base.metadata.create_all(bind=engine) # สร้างตารางใหม่
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def test_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


def test_register_user(test_client):
    response = test_client.post(
        "/users/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login_and_get_token(test_client):
    # Register first
    test_client.post(
        "/users/register",
        json={"username": "logintest", "email": "login@example.com", "password": "password123"},
    )
    # Then login
    response = test_client.post(
        "/users/token",
        data={"username": "logintest", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_province_endpoints(test_client):
    response = test_client.get("/campaign/provinces/น่าน")
    assert response.status_code == 200
    assert response.json()["province_type"] == "เมืองรอง"

def test_campaign_registration_unauthorized(test_client):
    response = test_client.post(
        "/campaign/register",
        json={"full_name": "Test Name", "id_card_number": "1234567890123", "target_province": "น่าน"},
    )
    assert response.status_code == 401 # Unauthorized

def test_campaign_registration_authorized(test_client):
    # Register and login to get a token
    test_client.post(
        "/users/register",
        json={"username": "campaignuser", "email": "campaign@example.com", "password": "password123"},
    )
    login_res = test_client.post(
        "/users/token",
        data={"username": "campaignuser", "password": "password123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Register for campaign
    response = test_client.post(
        "/campaign/register",
        headers=headers,
        json={"full_name": "Test Name", "id_card_number": "1234567890123", "target_province": "น่าน"},
    )
    assert response.status_code == 201
    assert "Successfully registered" in response.json()["message"]