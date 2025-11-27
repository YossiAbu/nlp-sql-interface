# backend/tests/test_auth.py
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from services.user_service import users_table, get_engine

# Mark all tests in this file to skip mocking (use real DB for auth)
pytestmark = pytest.mark.no_mock


@pytest.fixture(autouse=True)
def setup_and_cleanup_users():
    """Clean up users table before and after each test."""
    engine = get_engine()
    with engine.connect() as conn:
        # Clean up before test
        conn.execute(users_table.delete())
        conn.commit()
    
    yield  # Run the test
    
    # Clean up after test
    with engine.connect() as conn:
        conn.execute(users_table.delete())
        conn.commit()


# ============================================
# User Registration Tests
# ============================================

@pytest.mark.asyncio
async def test_register_user_success():
    """Test successful user registration."""
    payload = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123!"
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/register", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered successfully"


@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Test registration with duplicate email fails."""
    payload = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123!"
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register first user
        await ac.post("/register", json=payload)
        
        # Try to register again with same email
        response = await ac.post("/register", json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert "already registered" in data["detail"].lower()


@pytest.mark.asyncio
async def test_register_missing_fields():
    """Test registration with missing required fields."""
    payload = {
        "email": "john@example.com"
        # Missing full_name and password
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/register", json=payload)
    
    assert response.status_code == 422  # Validation error


# ============================================
# User Login Tests
# ============================================

@pytest.mark.asyncio
async def test_login_success():
    """Test successful login with valid credentials."""
    # First register a user
    register_payload = {
        "full_name": "Jane Smith",
        "email": "jane@example.com",
        "password": "MyPassword123!"
    }
    login_payload = {
        "email": "jane@example.com",
        "password": "MyPassword123!"
    }
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register
        await ac.post("/register", json=register_payload)
        
        # Login
        response = await ac.post("/login", json=login_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert data["full_name"] == "Jane Smith"
    
    # Check that cookie is set
    assert "user_id" in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password():
    """Test login fails with wrong password."""
    # First register a user
    register_payload = {
        "full_name": "Jane Smith",
        "email": "jane@example.com",
        "password": "CorrectPassword123!"
    }
    login_payload = {
        "email": "jane@example.com",
        "password": "WrongPassword123!"
    }
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register
        await ac.post("/register", json=register_payload)
        
        # Try to login with wrong password
        response = await ac.post("/login", json=login_payload)
    
    assert response.status_code == 401
    data = response.json()
    assert "invalid credentials" in data["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user():
    """Test login fails for non-existent user."""
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123!"
    }
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/login", json=login_payload)
    
    assert response.status_code == 401
    data = response.json()
    assert "invalid credentials" in data["detail"].lower()


@pytest.mark.asyncio
async def test_login_missing_fields():
    """Test login with missing required fields."""
    payload = {
        "email": "test@example.com"
        # Missing password
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/login", json=payload)
    
    assert response.status_code == 422  # Validation error


# ============================================
# User Logout Tests
# ============================================

@pytest.mark.asyncio
async def test_logout_success():
    """Test logout returns success response."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
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
    # Register and login
    register_payload = {
        "full_name": "Alice Johnson",
        "email": "alice@example.com",
        "password": "AlicePass123!"
    }
    login_payload = {
        "email": "alice@example.com",
        "password": "AlicePass123!"
    }
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register and login
        await ac.post("/register", json=register_payload)
        login_response = await ac.post("/login", json=login_payload)
        
        # Get cookies from login
        cookies = login_response.cookies
        
        # Call /me with authentication
        response = await ac.get("/me", cookies=cookies)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice Johnson"


@pytest.mark.asyncio
async def test_get_me_not_authenticated():
    """Test /me returns null values when not authenticated."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
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
    # Register and login
    register_payload = {
        "full_name": "Bob Wilson",
        "email": "bob@example.com",
        "password": "BobPass123!"
    }
    login_payload = {
        "email": "bob@example.com",
        "password": "BobPass123!"
    }
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register and login
        await ac.post("/register", json=register_payload)
        login_response = await ac.post("/login", json=login_payload)
        
        # Get cookies from login
        cookies = login_response.cookies
        
        # Access protected route
        response = await ac.get("/protected", cookies=cookies)
    
    assert response.status_code == 200
    data = response.json()
    assert "Welcome" in data["message"]


@pytest.mark.asyncio
async def test_protected_route_without_auth():
    """Test protected route blocked without authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
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
    
    register_payload = {
        "full_name": "Charlie Brown",
        "email": "charlie@example.com",
        "password": "PlainTextPassword123!"
    }
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/register", json=register_payload)
    
    # Verify password is hashed in DB
    user = get_user_by_email("charlie@example.com")
    assert user is not None
    assert user["password_hash"] != "PlainTextPassword123!"  # Should be hashed
    assert user["password_hash"].startswith("$2b$")  # bcrypt hash prefix