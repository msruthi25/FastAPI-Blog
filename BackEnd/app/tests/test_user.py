# test_user.py
import uuid
import pytest
from sqlalchemy import select
from app.model import User
from app.auth.hashing import hash_password
from app.routes import user_routes
from app.databaseSetup import get_db
from app.main import app
# ----------------------------
# Helper to create a test user
# ----------------------------
async def create_test_user(session):
    result = await session.execute(select(User).filter(User.email == "testuser@example.com"))
    user = result.scalar_one_or_none()

    if not user:
        password_hash = await hash_password("password123")
        user = User(
            username="testuser",
            email="testuser@example.com",
            password_hash=password_hash
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user

# ----------------------------
# Successful login
# ----------------------------
@pytest.mark.anyio
async def test_login_success(async_client, async_session):
    await create_test_user(async_session)

    payload = {"email": "testuser@example.com", "password": "password123"}
    response = await async_client.post("/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "testuser"
    assert "user_id" in data

# ----------------------------
# Invalid email
# ----------------------------
@pytest.mark.anyio
async def test_login_invalid_email(async_client):
    payload = {"email": "wrong@example.com", "password": "password123"}
    response = await async_client.post("/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

# ----------------------------
# Invalid password
# ----------------------------
@pytest.mark.anyio
async def test_login_invalid_password(async_client):
    payload = {"email": "testuser@example.com", "password": "wrongpassword"}
    response = await async_client.post("/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.anyio
async def test_login_server_error(async_client):    
    async def fake_get_db():
        yield  
        raise Exception("Forced server error") 
    app.dependency_overrides[get_db] = fake_get_db
    try:
        payload = {"email": "testuser@example.com", "password": "password123"}
        response = await async_client.post("/login", json=payload)
        assert response.status_code == 500
        assert "Internal Server Error" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()




@pytest.mark.anyio
async def test_register_success(async_client):
    unique_email = f"newuser_{uuid.uuid4()}@example.com"
    unique_username = f"newuser_{uuid.uuid4()}"
    payload = {
        "username": unique_username,
        "email": unique_email,
        "password": "password123"
    }
    response = await async_client.post("/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "User registered successfully" in data["message"]

@pytest.mark.anyio
async def test_register_duplicate_email(async_client):
    # First registration succeeds
    payload = {
        "username": "dupuser",
        "email": "dupuser@example.com",
        "password": "password123"
    }
    await async_client.post("/register", json=payload)

    # Second registration with same email should fail
    response = await async_client.post("/register", json=payload)
    assert response.status_code == 409
    assert "Email already exists" in response.json()["detail"]

@pytest.mark.anyio
async def test_register_server_error(async_client):
    # Override get_db to simulate server error
    async def fake_get_db():
        yield  # yield required for async generator
        raise Exception("Forced server error")  # raise inside generator

    app.dependency_overrides[get_db] = fake_get_db

    try:
        payload = {
            "username": "erroruser",
            "email": "erroruser@example.com",
            "password": "password123"
        }
        response = await async_client.post("/register", json=payload)
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()        