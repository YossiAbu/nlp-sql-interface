# backend/tests/test_real_db.py
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

# Use both markers: no_mock (use real services) + real_db (auto-skip in CI)
pytestmark = [pytest.mark.no_mock, pytest.mark.real_db]


@pytest.mark.asyncio
async def test_query_with_real_database():
    """Test /query endpoint with real PostgreSQL database."""
    payload = {"question": "Show top 5 players by rating"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/query", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "sql_query" in data
    assert data["status"] == "success"
    # With real data, you'll get actual results from your database
    assert len(data["raw_rows"]) > 0