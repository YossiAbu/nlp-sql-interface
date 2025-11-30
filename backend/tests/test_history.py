# backend/tests/test_history.py
"""Tests for history endpoints and functionality."""
import pytest
from httpx import AsyncClient
from main import app
from services.user_service import users_table, get_engine
from services.history_service import HistoryService
from schemas.history import HistoryCreate
from models.history import History
from services.db_service import get_session
from . import make_user_payload, make_login_payload, get_test_client

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


async def register_and_login(
    ac: AsyncClient,
    full_name: str = "Test User",
    email: str = "testuser@example.com",
    password: str = "TestPass123!"
) -> dict:
    """Helper to register and login a user, returns cookies."""
    register_payload = make_user_payload(full_name, email, password)
    login_payload = make_login_payload(email, password)
    
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
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.get("/history")
    
    assert response.status_code == 401
    data = response.json()
    assert "not authenticated" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_history_empty():
    """Test that /history returns empty list for new user."""
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
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
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        cookies = await register_and_login(ac)
        user_id = get_user_id_from_cookies(cookies)
        
        create_fake_history_entry(user_id, "Show all players")
        
        response = await ac.get("/history", cookies=cookies)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    
    entry = data["items"][0]
    assert entry["question"] == "Show all players"
    assert "id" in entry
    assert "sql_query" in entry
    assert "status" in entry
    assert "created_date" in entry


@pytest.mark.asyncio
async def test_get_history_pagination():
    """Test that /history pagination works correctly."""
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        cookies = await register_and_login(ac)
        user_id = get_user_id_from_cookies(cookies)
        
        for i in range(5):
            create_fake_history_entry(user_id, f"Query number {i}")
        
        response = await ac.get("/history?page=1&per_page=2", cookies=cookies)
        data = response.json()
        
        assert response.status_code == 200
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["total_pages"] == 3
        
        response2 = await ac.get("/history?page=2&per_page=2", cookies=cookies)
        data2 = response2.json()
        
        assert response2.status_code == 200
        assert len(data2["items"]) == 2
        assert data2["page"] == 2


@pytest.mark.asyncio
async def test_get_history_only_own_entries():
    """Test that users can only see their own history."""
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        cookies1 = await register_and_login(ac, "User One", "user1@example.com", "Pass123!")
        user1_id = get_user_id_from_cookies(cookies1)
        
        cookies2 = await register_and_login(ac, "User Two", "user2@example.com", "Pass123!")
        user2_id = get_user_id_from_cookies(cookies2)
        
        create_fake_history_entry(user1_id, "User 1 query")
        create_fake_history_entry(user2_id, "User 2 query")
        
        response1 = await ac.get("/history", cookies=cookies1)
        data1 = response1.json()
        
        assert data1["total"] == 1
        assert data1["items"][0]["question"] == "User 1 query"
        
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
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.delete("/history")
    
    assert response.status_code == 401
    data = response.json()
    assert "not authenticated" in data["detail"].lower()


@pytest.mark.asyncio
async def test_clear_history_success():
    """Test that DELETE /history clears all user's history."""
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        cookies = await register_and_login(ac)
        user_id = get_user_id_from_cookies(cookies)
        
        create_fake_history_entry(user_id, "Query 1")
        create_fake_history_entry(user_id, "Query 2")
        create_fake_history_entry(user_id, "Query 3")
        
        history_before = await ac.get("/history", cookies=cookies)
        assert history_before.json()["total"] == 3
        
        response = await ac.delete("/history", cookies=cookies)
        
        assert response.status_code == 200
        data = response.json()
        assert "Deleted 3" in data["message"]
        
        history_after = await ac.get("/history", cookies=cookies)
        assert history_after.json()["total"] == 0


@pytest.mark.asyncio
async def test_clear_history_only_own():
    """Test that clearing history only affects the user's own history."""
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        cookies1 = await register_and_login(ac, "User One", "user1@example.com", "Pass123!")
        user1_id = get_user_id_from_cookies(cookies1)
        
        cookies2 = await register_and_login(ac, "User Two", "user2@example.com", "Pass123!")
        user2_id = get_user_id_from_cookies(cookies2)
        
        create_fake_history_entry(user1_id, "User 1 query")
        create_fake_history_entry(user2_id, "User 2 query")
        
        await ac.delete("/history", cookies=cookies1)
        
        history1 = await ac.get("/history", cookies=cookies1)
        assert history1.json()["total"] == 0
        
        history2 = await ac.get("/history", cookies=cookies2)
        assert history2.json()["total"] == 1


# ============================================
# Query Saves to History Tests
# ============================================

@pytest.mark.asyncio
async def test_query_saves_to_history_when_authenticated():
    """Test that making a query saves it to history when logged in."""
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        cookies = await register_and_login(ac)
        
        query_response = await ac.post(
            "/query", 
            json={"question": "Show top 5 players"}, 
            cookies=cookies
        )
        
        assert query_response.status_code == 200
        
        history_response = await ac.get("/history", cookies=cookies)
        history = history_response.json()
        
        assert history["total"] == 1
        assert history["items"][0]["question"] == "Show top 5 players"
        assert "sql_query" in history["items"][0]
        assert "status" in history["items"][0]


@pytest.mark.asyncio
async def test_query_not_saved_when_anonymous():
    """Test that making a query does NOT save to history when not logged in."""
    transport, base_url = get_test_client(app)
    
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        cookies = await register_and_login(ac)
    
    async with AsyncClient(transport=transport, base_url=base_url) as ac_anonymous:
        query_response = await ac_anonymous.post(
            "/query", 
            json={"question": "Anonymous query"}
        )
        assert query_response.status_code == 200
    
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        history_response = await ac.get("/history", cookies=cookies)
        history = history_response.json()
        
        assert history["total"] == 0


@pytest.mark.asyncio
async def test_history_entry_structure():
    """Test that history entry contains all expected fields."""
    transport, base_url = get_test_client(app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        cookies = await register_and_login(ac)
        user_id = get_user_id_from_cookies(cookies)
        
        create_fake_history_entry(user_id, "Test question")
        
        history_response = await ac.get("/history", cookies=cookies)
        history = history_response.json()
        
        entry = history["items"][0]
        
        assert "id" in entry
        assert "user_id" in entry
        assert "question" in entry
        assert "sql_query" in entry
        assert "status" in entry
        assert "execution_time" in entry
        assert "results" in entry
        assert "raw_rows" in entry
        assert "created_date" in entry
        
        assert entry["question"] == "Test question"
        assert entry["status"] == "success"
        assert entry["sql_query"] == "SELECT * FROM players LIMIT 5"
