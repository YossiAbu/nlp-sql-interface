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


# ============================================
# Fixtures
# ============================================

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


# ============================================
# Helper Functions
# ============================================

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

class TestGetHistory:
    """Tests for GET /history endpoint."""
    
    @pytest.mark.asyncio
    async def test_returns_401_when_unauthenticated(self):
        """Test that /history returns 401 when not authenticated."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.get("/history")
        
        assert response.status_code == 401
        data = response.json()
        assert "not authenticated" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_returns_empty_list_for_new_user(self):
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
    async def test_returns_user_history_entries(self):
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
    async def test_pagination_works_correctly(self):
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
    async def test_users_only_see_own_entries(self):
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

class TestClearHistory:
    """Tests for DELETE /history endpoint."""
    
    @pytest.mark.asyncio
    async def test_returns_401_when_unauthenticated(self):
        """Test that DELETE /history returns 401 when not authenticated."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.delete("/history")
        
        assert response.status_code == 401
        data = response.json()
        assert "not authenticated" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_clears_all_user_history(self):
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
    async def test_only_clears_own_history(self):
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

class TestQuerySavesToHistory:
    """Tests for query-to-history integration."""
    
    @pytest.mark.asyncio
    async def test_saves_when_authenticated(self):
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
    async def test_not_saved_when_anonymous(self):
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


# ============================================
# History Entry Structure Tests
# ============================================

class TestHistoryEntryStructure:
    """Tests for history entry data structure."""
    
    @pytest.mark.asyncio
    async def test_contains_all_expected_fields(self):
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


# ============================================
# HistoryService Unit Tests (Direct DB Access)
# ============================================

def create_history_entry_and_get_id(user_id: str, question: str = "Test question") -> str:
    """Helper to create a history entry and return its ID."""
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
        entry = HistoryService.create_history_entry(db, user_id, history_data)
        return entry.id
    finally:
        db.close()


class TestHistoryServiceGetById:
    """Tests for HistoryService.get_history_by_id method."""
    
    @pytest.mark.asyncio
    async def test_returns_entry_when_found(self):
        """Test get_history_by_id returns the entry when it exists."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            cookies = await register_and_login(ac)
            user_id = get_user_id_from_cookies(cookies)
        
        # Create entry and get its ID
        entry_id = create_history_entry_and_get_id(user_id, "Find me")
        
        # Retrieve it using the service
        db = get_session()
        try:
            found = HistoryService.get_history_by_id(db, entry_id, user_id)
            assert found is not None
            assert found.question == "Find me"
            assert found.id == entry_id
        finally:
            db.close()
    
    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Test get_history_by_id returns None for non-existent entry."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            cookies = await register_and_login(ac)
            user_id = get_user_id_from_cookies(cookies)
        
        db = get_session()
        try:
            result = HistoryService.get_history_by_id(db, "non-existent-id", user_id)
            assert result is None
        finally:
            db.close()
    
    @pytest.mark.asyncio
    async def test_returns_none_for_other_users_entry(self):
        """Test get_history_by_id returns None when accessing another user's entry."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            # Create two users
            cookies1 = await register_and_login(ac, "User One", "user1@example.com", "Pass123!")
            user1_id = get_user_id_from_cookies(cookies1)
            
            cookies2 = await register_and_login(ac, "User Two", "user2@example.com", "Pass123!")
            user2_id = get_user_id_from_cookies(cookies2)
        
        # Create entry for user1
        entry_id = create_history_entry_and_get_id(user1_id, "User1 private query")
        
        # User2 should not be able to access it
        db = get_session()
        try:
            result = HistoryService.get_history_by_id(db, entry_id, user2_id)
            assert result is None
        finally:
            db.close()


class TestHistoryServiceDeleteEntry:
    """Tests for HistoryService.delete_history_entry method."""
    
    @pytest.mark.asyncio
    async def test_deletes_own_entry_successfully(self):
        """Test delete_history_entry returns True and deletes the entry."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            cookies = await register_and_login(ac)
            user_id = get_user_id_from_cookies(cookies)
        
        # Create entry
        entry_id = create_history_entry_and_get_id(user_id, "To be deleted")
        
        db = get_session()
        try:
            # Delete it
            result = HistoryService.delete_history_entry(db, entry_id, user_id)
            assert result is True
            
            # Verify it's gone
            found = HistoryService.get_history_by_id(db, entry_id, user_id)
            assert found is None
        finally:
            db.close()
    
    @pytest.mark.asyncio
    async def test_returns_false_for_nonexistent_entry(self):
        """Test delete_history_entry returns False for non-existent entry."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            cookies = await register_and_login(ac)
            user_id = get_user_id_from_cookies(cookies)
        
        db = get_session()
        try:
            result = HistoryService.delete_history_entry(db, "non-existent-id", user_id)
            assert result is False
        finally:
            db.close()
    
    @pytest.mark.asyncio
    async def test_cannot_delete_other_users_entry(self):
        """Test delete_history_entry returns False when trying to delete another user's entry."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            # Create two users
            cookies1 = await register_and_login(ac, "User One", "user1@example.com", "Pass123!")
            user1_id = get_user_id_from_cookies(cookies1)
            
            cookies2 = await register_and_login(ac, "User Two", "user2@example.com", "Pass123!")
            user2_id = get_user_id_from_cookies(cookies2)
        
        # Create entry for user1
        entry_id = create_history_entry_and_get_id(user1_id, "User1 entry")
        
        db = get_session()
        try:
            # User2 tries to delete it - should fail
            result = HistoryService.delete_history_entry(db, entry_id, user2_id)
            assert result is False
            
            # Entry should still exist for user1
            found = HistoryService.get_history_by_id(db, entry_id, user1_id)
            assert found is not None
        finally:
            db.close()
