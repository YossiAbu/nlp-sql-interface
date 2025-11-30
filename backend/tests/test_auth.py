# backend/tests/test_auth.py
import pytest
from httpx import AsyncClient
from main import app
from services.user_service import users_table, get_engine
from . import make_user_payload, make_login_payload, get_test_client

# Mark all tests in this file to skip mocking (use real DB for auth)
pytestmark = pytest.mark.no_mock


@pytest.fixture(autouse=True)
def setup_and_cleanup_users():
    """Clean up users table before and after each test."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(users_table.delete())
        conn.commit()
    
    yield  # Run the test
    
    with engine.connect() as conn:
        conn.execute(users_table.delete())
        conn.commit()


# ============================================
# User Registration Tests
# ============================================

@pytest.mark.asyncio
async def test_register_user_success():
    """Test successful user registration."""
    payload = make_user_payload("John Doe", "john@example.com", "SecurePass123!")
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.post("/register", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered successfully"


@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Test registration with duplicate email fails."""
    payload = make_user_payload("John Doe", "john@example.com", "SecurePass123!")
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        await ac.post("/register", json=payload)
        response = await ac.post("/register", json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert "already registered" in data["detail"].lower()


@pytest.mark.asyncio
async def test_register_missing_fields():
    """Test registration with missing required fields."""
    payload = {"email": "john@example.com"}
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.post("/register", json=payload)
    
    assert response.status_code == 422


# ============================================
# User Login Tests
# ============================================

@pytest.mark.asyncio
async def test_login_success():
    """Test successful login with valid credentials."""
    email, password = "jane@example.com", "MyPassword123!"
    register_payload = make_user_payload("Jane Smith", email, password)
    login_payload = make_login_payload(email, password)
    
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        await ac.post("/register", json=register_payload)
        response = await ac.post("/login", json=login_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert data["full_name"] == "Jane Smith"
    assert "user_id" in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password():
    """Test login fails with wrong password."""
    email = "jane@example.com"
    register_payload = make_user_payload("Jane Smith", email, "CorrectPassword123!")
    login_payload = make_login_payload(email, "WrongPassword123!")
    
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        await ac.post("/register", json=register_payload)
        response = await ac.post("/login", json=login_payload)
    
    assert response.status_code == 401
    data = response.json()
    assert "invalid credentials" in data["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user():
    """Test login fails for non-existent user."""
    login_payload = make_login_payload("nonexistent@example.com", "SomePassword123!")
    
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.post("/login", json=login_payload)
    
    assert response.status_code == 401
    data = response.json()
    assert "invalid credentials" in data["detail"].lower()


@pytest.mark.asyncio
async def test_login_missing_fields():
    """Test login with missing required fields."""
    payload = {"email": "test@example.com"}
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.post("/login", json=payload)
    
    assert response.status_code == 422


# ============================================
# User Logout Tests
# ============================================

@pytest.mark.asyncio
async def test_logout_success():
    """Test logout returns success response."""
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.post("/logout")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logged out successfully"


# ============================================
# Get Current User Tests (/me)
# ============================================

@pytest.mark.asyncio
async def test_get_me_authenticated():
    """Test /me returns user info when authenticated."""
    email, password = "alice@example.com", "AlicePass123!"
    register_payload = make_user_payload("Alice Johnson", email, password)
    login_payload = make_login_payload(email, password)
    
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        await ac.post("/register", json=register_payload)
        login_response = await ac.post("/login", json=login_payload)
        cookies = login_response.cookies
        
        response = await ac.get("/me", cookies=cookies)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice Johnson"


@pytest.mark.asyncio
async def test_get_me_not_authenticated():
    """Test /me returns null values when not authenticated."""
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.get("/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] is None
    assert data["full_name"] is None


# ============================================
# Protected Route Tests
# ============================================

@pytest.mark.asyncio
async def test_protected_route_with_auth():
    """Test protected route accessible with authentication."""
    email, password = "bob@example.com", "BobPass123!"
    register_payload = make_user_payload("Bob Wilson", email, password)
    login_payload = make_login_payload(email, password)
    
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        await ac.post("/register", json=register_payload)
        login_response = await ac.post("/login", json=login_payload)
        cookies = login_response.cookies
        
        response = await ac.get("/protected", cookies=cookies)
    
    assert response.status_code == 200
    data = response.json()
    assert "Welcome" in data["message"]


@pytest.mark.asyncio
async def test_protected_route_without_auth():
    """Test protected route blocked without authentication."""
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.get("/protected")
    
    assert response.status_code == 401
    data = response.json()
    assert "not authenticated" in data["detail"].lower()


# ============================================
# Password Security Tests
# ============================================

@pytest.mark.asyncio
async def test_password_is_hashed():
    """Test that passwords are hashed in database, not stored in plain text."""
    from services.user_service import get_user_by_email
    
    email, password = "charlie@example.com", "PlainTextPassword123!"
    register_payload = make_user_payload("Charlie Brown", email, password)
    
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        await ac.post("/register", json=register_payload)
    
    user = get_user_by_email(email)
    assert user is not None
    assert user["password_hash"] != password
    assert user["password_hash"].startswith("$2b$")
