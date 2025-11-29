# backend/tests/test_history.py
"""Tests for history endpoints and functionality."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from services.user_service import users_table, get_engine
from services.history_service import HistoryService
from schemas.history import HistoryCreate
from models.history import History
from services.db_service import get_session

# Mark all tests to skip mocking (use real DB)
pytestmark = pytest.mark.no_mock


@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Clean up users and history tables before and after each test."""
    engine = get_engine()
    
    # Clean up before test
    db = get_session()
    try:
        db.query(History).delete()
        db.commit()
    finally:
        db.close()
    
    with engine.connect() as conn:
        conn.execute(users_table.delete())
        conn.commit()
    
    yield  # Run the test
    
    # Clean up after test
    db = get_session()
    try:
        db.query(History).delete()
        db.commit()
    finally:
        db.close()
    
    with engine.connect() as conn:
        conn.execute(users_table.delete())
        conn.commit()


async def register_and_login(ac: AsyncClient) -> dict:
    """Helper to register and login a user, returns cookies and user_id."""
    register_payload = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPass123!"
    }
    login_payload = {
        "email": "testuser@example.com",
        "password": "TestPass123!"
    }
    
    await ac.post("/register", json=register_payload)
    login_response = await ac.post("/login", json=login_payload)
    return login_response.cookies


def create_fake_history_entry(user_id: str, question: str = "Test question") -> None:
    """Helper to directly insert a history entry without calling OpenAI."""
    db = get_session()
    try:
        history_data = HistoryCreate(
            question=question,
            sql_query="SELECT * FROM players LIMIT 5",
            status="success",
            execution_time=100,
            results="Test results",
            raw_rows=[{"name": "Test", "ovr": 90}],
            error_message=None
        )
        HistoryService.create_history_entry(db, user_id, history_data)
    finally:
        db.close()


def get_user_id_from_cookies(cookies) -> str:
    """Extract user_id from cookies."""
    return cookies.get("user_id")


# ============================================
# Get History Tests
# ============================================

@pytest.mark.asyncio
async def test_get_history_unauthenticated():
    """Test that /history returns 401 when not authenticated."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/history")
    
    assert response.status_code == 401
    data = response.json()
    assert "not authenticated" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_history_empty():
    """Test that /history returns empty list for new user."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        cookies = await register_and_login(ac)
        
        response = await ac.get("/history", cookies=cookies)
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["total_pages"] == 0


@pytest.mark.asyncio
async def test_get_history_with_entries():
    """Test that /history returns user's query history."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        cookies = await register_and_login(ac)
        user_id = get_user_id_from_cookies(cookies)
        
        # Insert history directly (no OpenAI call)
        create_fake_history_entry(user_id, "Show all players")
        
        # Get history
        response = await ac.get("/history", cookies=cookies)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    
    # Verify history entry structure
    entry = data["items"][0]
    assert entry["question"] == "Show all players"
    assert "id" in entry
    assert "sql_query" in entry
    assert "status" in entry
    assert "created_date" in entry


@pytest.mark.asyncio
async def test_get_history_pagination():
    """Test that /history pagination works correctly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        cookies = await register_and_login(ac)
        user_id = get_user_id_from_cookies(cookies)
        
        # Insert multiple history entries directly
        for i in range(5):
            create_fake_history_entry(user_id, f"Query number {i}")
        
        # Get first page with 2 items
        response = await ac.get("/history?page=1&per_page=2", cookies=cookies)
        data = response.json()
        
        assert response.status_code == 200
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["total_pages"] == 3
        
        # Get second page
        response2 = await ac.get("/history?page=2&per_page=2", cookies=cookies)
        data2 = response2.json()
        
        assert response2.status_code == 200
        assert len(data2["items"]) == 2
        assert data2["page"] == 2


@pytest.mark.asyncio
async def test_get_history_only_own_entries():
    """Test that users can only see their own history."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # User 1: register, login
        await ac.post("/register", json={
            "full_name": "User One",
            "email": "user1@example.com",
            "password": "Pass123!"
        })
        login1 = await ac.post("/login", json={
            "email": "user1@example.com",
            "password": "Pass123!"
        })
        cookies1 = login1.cookies
        user1_id = get_user_id_from_cookies(cookies1)
        
        # User 2: register, login
        await ac.post("/register", json={
            "full_name": "User Two",
            "email": "user2@example.com",
            "password": "Pass123!"
        })
        login2 = await ac.post("/login", json={
            "email": "user2@example.com",
            "password": "Pass123!"
        })
        cookies2 = login2.cookies
        user2_id = get_user_id_from_cookies(cookies2)
        
        # Insert history for each user
        create_fake_history_entry(user1_id, "User 1 query")
        create_fake_history_entry(user2_id, "User 2 query")
        
        # User 1 should only see their own history
        response1 = await ac.get("/history", cookies=cookies1)
        data1 = response1.json()
        
        assert data1["total"] == 1
        assert data1["items"][0]["question"] == "User 1 query"
        
        # User 2 should only see their own history
        response2 = await ac.get("/history", cookies=cookies2)
        data2 = response2.json()
        
        assert data2["total"] == 1
        assert data2["items"][0]["question"] == "User 2 query"


# ============================================
# Clear History Tests
# ============================================

@pytest.mark.asyncio
async def test_clear_history_unauthenticated():
    """Test that DELETE /history returns 401 when not authenticated."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/history")
    
    assert response.status_code == 401
    data = response.json()
    assert "not authenticated" in data["detail"].lower()


@pytest.mark.asyncio
async def test_clear_history_success():
    """Test that DELETE /history clears all user's history."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        cookies = await register_and_login(ac)
        user_id = get_user_id_from_cookies(cookies)
        
        # Insert history entries directly
        create_fake_history_entry(user_id, "Query 1")
        create_fake_history_entry(user_id, "Query 2")
        create_fake_history_entry(user_id, "Query 3")
        
        # Verify history exists
        history_before = await ac.get("/history", cookies=cookies)
        assert history_before.json()["total"] == 3
        
        # Clear history
        response = await ac.delete("/history", cookies=cookies)
        
        assert response.status_code == 200
        data = response.json()
        assert "Deleted 3" in data["message"]
        
        # Verify history is empty
        history_after = await ac.get("/history", cookies=cookies)
        assert history_after.json()["total"] == 0


@pytest.mark.asyncio
async def test_clear_history_only_own():
    """Test that clearing history only affects the user's own history."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # User 1: register, login
        await ac.post("/register", json={
            "full_name": "User One",
            "email": "user1@example.com",
            "password": "Pass123!"
        })
        login1 = await ac.post("/login", json={
            "email": "user1@example.com",
            "password": "Pass123!"
        })
        cookies1 = login1.cookies
        user1_id = get_user_id_from_cookies(cookies1)
        
        # User 2: register, login
        await ac.post("/register", json={
            "full_name": "User Two",
            "email": "user2@example.com",
            "password": "Pass123!"
        })
        login2 = await ac.post("/login", json={
            "email": "user2@example.com",
            "password": "Pass123!"
        })
        cookies2 = login2.cookies
        user2_id = get_user_id_from_cookies(cookies2)
        
        # Insert history for each user
        create_fake_history_entry(user1_id, "User 1 query")
        create_fake_history_entry(user2_id, "User 2 query")
        
        # User 1 clears their history
        await ac.delete("/history", cookies=cookies1)
        
        # User 1's history should be empty
        history1 = await ac.get("/history", cookies=cookies1)
        assert history1.json()["total"] == 0
        
        # User 2's history should still exist
        history2 = await ac.get("/history", cookies=cookies2)
        assert history2.json()["total"] == 1


# ============================================
# Query Saves to History Tests
# ============================================

@pytest.mark.asyncio
async def test_query_saves_to_history_when_authenticated():
    """Test that making a query saves it to history when logged in."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        cookies = await register_and_login(ac)
        
        # Make a query (this one DOES call the real /query endpoint)
        query_response = await ac.post(
            "/query", 
            json={"question": "Show top 5 players"}, 
            cookies=cookies
        )
        
        assert query_response.status_code == 200
        
        # Check history
        history_response = await ac.get("/history", cookies=cookies)
        history = history_response.json()
        
        assert history["total"] == 1
        assert history["items"][0]["question"] == "Show top 5 players"
        assert "sql_query" in history["items"][0]
        assert "status" in history["items"][0]


@pytest.mark.asyncio
async def test_query_not_saved_when_anonymous():
    """Test that making a query does NOT save to history when not logged in."""
    transport = ASGITransport(app=app)
    
    # First client: register and login to create user
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        cookies = await register_and_login(ac)
    
    # Second client: make anonymous query (completely fresh client, no cookies)
    async with AsyncClient(transport=transport, base_url="http://test") as ac_anonymous:
        query_response = await ac_anonymous.post(
            "/query", 
            json={"question": "Anonymous query"}
        )
        assert query_response.status_code == 200
    
    # Third client: check history for the user (should be empty)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        history_response = await ac.get("/history", cookies=cookies)
        history = history_response.json()
        
        assert history["total"] == 0


@pytest.mark.asyncio
async def test_history_entry_structure():
    """Test that history entry contains all expected fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        cookies = await register_and_login(ac)
        user_id = get_user_id_from_cookies(cookies)
        
        # Insert a complete history entry
        create_fake_history_entry(user_id, "Test question")
        
        # Get history
        history_response = await ac.get("/history", cookies=cookies)
        history = history_response.json()
        
        entry = history["items"][0]
        
        # Verify all expected fields exist
        assert "id" in entry
        assert "user_id" in entry
        assert "question" in entry
        assert "sql_query" in entry
        assert "status" in entry
        assert "execution_time" in entry
        assert "results" in entry
        assert "raw_rows" in entry
        assert "created_date" in entry
        
        # Verify field values
        assert entry["question"] == "Test question"
        assert entry["status"] == "success"
        assert entry["sql_query"] == "SELECT * FROM players LIMIT 5"