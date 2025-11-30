# backend/tests/test_auth.py
"""Tests for authentication endpoints and functionality."""
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

class TestUserRegistration:
    """Tests for /register endpoint."""
    
    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful user registration."""
        payload = make_user_payload("John Doe", "john@example.com", "SecurePass123!")
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.post("/register", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered successfully"
    
    @pytest.mark.asyncio
    async def test_duplicate_email_fails(self):
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
    async def test_missing_fields_fails(self):
        """Test registration with missing required fields."""
        payload = {"email": "john@example.com"}
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.post("/register", json=payload)
        
        assert response.status_code == 422


# ============================================
# User Login Tests
# ============================================

class TestUserLogin:
    """Tests for /login endpoint."""
    
    @pytest.mark.asyncio
    async def test_success(self):
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
    async def test_wrong_password_fails(self):
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
    async def test_nonexistent_user_fails(self):
        """Test login fails for non-existent user."""
        login_payload = make_login_payload("nonexistent@example.com", "SomePassword123!")
        
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.post("/login", json=login_payload)
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid credentials" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_missing_fields_fails(self):
        """Test login with missing required fields."""
        payload = {"email": "test@example.com"}
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.post("/login", json=payload)
        
        assert response.status_code == 422


# ============================================
# User Logout Tests
# ============================================

class TestUserLogout:
    """Tests for /logout endpoint."""
    
    @pytest.mark.asyncio
    async def test_success(self):
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

class TestGetCurrentUser:
    """Tests for /me endpoint."""
    
    @pytest.mark.asyncio
    async def test_returns_user_info_when_authenticated(self):
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
    async def test_returns_null_when_not_authenticated(self):
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

class TestProtectedRoute:
    """Tests for /protected endpoint."""
    
    @pytest.mark.asyncio
    async def test_accessible_with_authentication(self):
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
    async def test_blocked_without_authentication(self):
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

class TestPasswordSecurity:
    """Tests for password security."""
    
    @pytest.mark.asyncio
    async def test_password_is_hashed_in_database(self):
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
