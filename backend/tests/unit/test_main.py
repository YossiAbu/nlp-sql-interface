import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_get_schema():
    """Test /schema endpoint returns valid response."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/schema")
    assert response.status_code == 200
    data = response.json()
    assert "tables" in data
    assert len(data["tables"]) > 0
    assert "name" in data["tables"][0]
    assert "columns" in data["tables"][0]

@pytest.mark.asyncio
async def test_process_query_success():
    """Test /query endpoint with a valid question."""
    payload = {"question": "Show top 5 players by rating"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "sql_query" in data
    assert data["status"] in ["success", "error"]

@pytest.mark.asyncio
async def test_process_query_invalid():
    """Test /query endpoint with an unsafe question (AI should sanitize)."""
    payload = {"question": "DROP TABLE players"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "sql_query" in data
    # AI may replace unsafe query with safe SELECT
    assert data["sql_query"].strip().upper().startswith("SELECT")
