# backend/tests/test_schema.py
"""Tests for schema endpoints."""
import pytest
from httpx import AsyncClient
from main import app
from . import get_test_client


class TestSchemaEndpoint:
    """Tests for /schema endpoint."""
    
    @pytest.mark.asyncio
    async def test_returns_valid_schema_response(self):
        """Test /schema endpoint returns valid response."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.get("/schema")
        
        assert response.status_code == 200
        data = response.json()
        assert "tables" in data
        assert len(data["tables"]) > 0
        assert "name" in data["tables"][0]
        assert "columns" in data["tables"][0]
    
    @pytest.mark.asyncio
    async def test_schema_table_has_columns(self):
        """Test schema tables contain column definitions."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.get("/schema")
        
        assert response.status_code == 200
        data = response.json()
        table = data["tables"][0]
        assert len(table["columns"]) > 0


class TestRefreshSchemaEndpoint:
    """Tests for /refresh-schema endpoint."""
    
    @pytest.mark.asyncio
    async def test_returns_refreshed_schema(self):
        """Test /refresh-schema endpoint returns schema."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.get("/refresh-schema")
        
        assert response.status_code == 200
        data = response.json()
        assert "tables" in data
        assert len(data["tables"]) > 0
    
    @pytest.mark.asyncio
    async def test_schema_refresh_flow(self):
        """Test schema refresh and retrieval flow."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
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
            
            # Ensure same structure
            assert set(schema1.keys()) == set(refreshed_schema.keys())

