import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from services.query_service import apply_alias_mapping, extract_column_names

# Main
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


# Query
def test_apply_alias_mapping():
    """Test alias mapping replaces terms correctly."""
    question = "Show me all footballers"
    mapped = apply_alias_mapping(question)
    assert "players" in mapped.lower()
    assert mapped != question  # Should be changed

def test_apply_alias_mapping_no_change():
    """Test alias mapping leaves unknown words unchanged."""
    question = "Show me all astronauts"
    mapped = apply_alias_mapping(question)
    assert mapped == question

def test_extract_column_names_simple():
    """Test column extraction from simple SQL."""
    sql = "SELECT name, ovr FROM players"
    columns = extract_column_names(sql)
    assert columns == ["name", "ovr"]

def test_extract_column_names_default():
    """Test default columns when SQL parse fails."""
    sql = "INVALID SQL"
    columns = extract_column_names(sql)
    assert columns == ["rank", "name", "ovr", "position", "nation", "team"]
