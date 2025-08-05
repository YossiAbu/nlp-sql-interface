import pytest
from httpx import AsyncClient, ASGITransport
from main import app

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
