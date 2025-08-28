import pytest
from fastapi.testclient import TestClient
from app.utils.security import hash_password
from app.models.user import User


@pytest.fixture
def test_user(db_session):
    user = User(
        username="naomi",
        email="naomi@example.com",
        hashed_password=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_login_success(client: TestClient, test_user: User):
    response = client.post("/api/v1/auth/login", json={"username": "naomi", "password": "password123"})
    assert response.status_code == 200
    assert "accessToken" in response.json()


def test_login_failure(client: TestClient):
    response = client.post("/api/v1/auth/login", json={"username": "bad", "password": "bad"})
    assert response.status_code == 401
