from services.query_service import handle_query
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

def test_handle_query_with_mock():
    """Test handle_query directly using the mocked DB chain"""
    question = "Who are the best players?"
    result = handle_query(question)

    # Check QueryResponse fields
    assert result.sql_query.strip().upper() == "SELECT NAME, OVR FROM PLAYERS LIMIT 3"
    assert result.results == "Top players list"
    assert result.status == "success"
    assert isinstance(result.execution_time, int)
    assert result.raw_rows == [
        {"name": "Messi", "ovr": 93},
        {"name": "Ronaldo", "ovr": 92},
        {"name": "Mbappe", "ovr": 91}
    ]


@pytest.mark.asyncio
async def test_query_full_output():
    """Integration test for /query endpoint with full expected output."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/query", json={"question": "Show best players"})
    assert response.status_code == 200
    data = response.json()

    # Exact values from our FakeDBChain mock
    assert data["sql_query"].strip().upper() == "SELECT NAME, OVR FROM PLAYERS LIMIT 3"
    assert data["results"] == "Top players list"
    assert data["status"] == "success"
    assert isinstance(data["execution_time"], int)
    assert data["raw_rows"] == [
        {"name": "Messi", "ovr": 93},
        {"name": "Ronaldo", "ovr": 92},
        {"name": "Mbappe", "ovr": 91}
    ]


@pytest.mark.asyncio
async def test_schema_refresh_flow():
    """Integration test for schema refresh and retrieval."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # First schema call
        resp1 = await ac.get("/schema")
        assert resp1.status_code == 200
        schema1 = resp1.json()
        assert "tables" in schema1 and len(schema1["tables"]) > 0

        # Refresh schema
        resp_refresh = await ac.get("/refresh-schema")
        assert resp_refresh.status_code == 200
        refreshed_schema = resp_refresh.json()
        assert "tables" in refreshed_schema and len(refreshed_schema["tables"]) > 0

        # In a real DB, we’d check that schema1 != refreshed_schema if schema changed
        # Here, just ensure same structure
        assert set(schema1.keys()) == set(refreshed_schema.keys())


@pytest.mark.asyncio
async def test_query_integration_sanitizes_malicious_input():
    """Integration test to ensure malicious input is sanitized into safe SQL."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/query", json={"question": "DROP TABLE players"})
    assert response.status_code == 200
    data = response.json()

    # Should still return safe SELECT due to AI mock
    assert data["sql_query"].strip().upper().startswith("SELECT")
    assert data["status"] == "success"
