import pytest
from httpx import AsyncClient, ASGITransport
from main import app

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
