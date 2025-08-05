import pytest
from httpx import AsyncClient, ASGITransport
from main import app


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
