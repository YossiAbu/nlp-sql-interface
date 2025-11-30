# backend/tests/test_query.py
"""Tests for query endpoint and query service functions."""
import pytest
from httpx import AsyncClient
from main import app
from services.query_service import (
    handle_query,
    apply_alias_mapping,
    extract_column_names,
    format_raw_rows,
    clean_sql_query
)
from . import get_test_client


# ============================================
# Query Service Unit Tests
# ============================================

class TestApplyAliasMapping:
    """Tests for alias mapping functionality."""
    
    def test_replaces_footballers_with_players(self):
        """Test alias mapping replaces terms correctly."""
        question = "Show me all footballers"
        mapped = apply_alias_mapping(question)
        assert "players" in mapped.lower()
        assert mapped != question
    
    def test_leaves_unknown_words_unchanged(self):
        """Test alias mapping leaves unknown words unchanged."""
        question = "Show me all astronauts"
        mapped = apply_alias_mapping(question)
        assert mapped == question
    
    def test_replaces_multiple_aliases(self):
        """Test multiple alias replacements in one question."""
        question = "Show footballers with high overall rating"
        mapped = apply_alias_mapping(question)
        assert "players" in mapped.lower()
        assert "ovr" in mapped.lower()
    
    def test_case_insensitive_replacement(self):
        """Test alias replacement is case insensitive."""
        question = "Show FOOTBALLERS"
        mapped = apply_alias_mapping(question)
        assert "players" in mapped.lower()


class TestExtractColumnNames:
    """Tests for SQL column name extraction."""
    
    def test_extracts_simple_columns(self):
        """Test column extraction from simple SQL."""
        sql = "SELECT name, ovr FROM players"
        columns = extract_column_names(sql)
        assert columns == ["name", "ovr"]
    
    def test_returns_defaults_for_invalid_sql(self):
        """Test default columns when SQL parse fails."""
        sql = "INVALID SQL"
        columns = extract_column_names(sql)
        assert columns == ["rank", "name", "ovr", "position", "nation", "team"]
    
    def test_returns_defaults_for_empty_sql(self):
        """Test default columns for empty SQL."""
        columns = extract_column_names("")
        assert columns == ["rank", "name", "ovr", "position", "nation", "team"]
    
    def test_handles_star_select(self):
        """Test column extraction for SELECT *."""
        sql = "SELECT * FROM players"
        columns = extract_column_names(sql)
        assert columns == ["rank", "name", "ovr", "position", "nation", "team"]
    
    def test_handles_columns_with_aliases(self):
        """Test column extraction with AS aliases extracts the alias name."""
        sql = "SELECT name as player_name, ovr as rating FROM players"
        columns = extract_column_names(sql)
        # The function extracts the alias (part after 'as')
        assert "player_name" in columns
        assert "rating" in columns


class TestFormatRawRows:
    """Tests for raw row formatting."""
    
    def test_formats_rows_correctly(self):
        """Test basic row formatting."""
        raw = [("Messi", 93), ("Ronaldo", 92)]
        cols = ["name", "ovr"]
        result = format_raw_rows(raw, cols)
        assert result == [
            {"name": "Messi", "ovr": 93},
            {"name": "Ronaldo", "ovr": 92}
        ]
    
    def test_returns_empty_for_empty_input(self):
        """Test empty input returns empty list."""
        assert format_raw_rows([], ["name"]) == []
        assert format_raw_rows([("a",)], []) == []
    
    def test_handles_mismatched_columns(self):
        """Test when more values than column names."""
        raw = [("Messi", 93, "Argentina")]
        cols = ["name", "ovr"]
        result = format_raw_rows(raw, cols)
        assert result == [{"name": "Messi", "ovr": 93}]


class TestCleanSqlQuery:
    """Tests for SQL query cleaning/sanitization."""
    
    def test_removes_markdown_code_blocks(self):
        """Test removal of markdown SQL code blocks."""
        sql = "```sql\nSELECT * FROM players\n```"
        cleaned = clean_sql_query(sql)
        assert "```" not in cleaned
        assert "SELECT" in cleaned.upper()
    
    def test_removes_sqlquery_prefix(self):
        """Test removal of SQLQuery: prefix."""
        sql = "SQLQuery: SELECT name FROM players"
        cleaned = clean_sql_query(sql)
        assert "SQLQuery:" not in cleaned
        assert "SELECT" in cleaned.upper()
    
    def test_handles_empty_input(self):
        """Test empty input returns empty string."""
        assert clean_sql_query("") == ""
    
    def test_handles_none_input(self):
        """Test None input returns empty string."""
        assert clean_sql_query(None) == ""
    
    def test_preserves_valid_sql(self):
        """Test valid SQL is preserved."""
        sql = "SELECT name, ovr FROM players WHERE ovr > 90"
        cleaned = clean_sql_query(sql)
        assert "SELECT" in cleaned.upper()
        assert "name" in cleaned


class TestHandleQuery:
    """Tests for the main handle_query function."""
    
    def test_returns_query_response_with_mock(self):
        """Test handle_query returns expected QueryResponse."""
        question = "Who are the best players?"
        result = handle_query(question)
        
        assert result.sql_query.strip().upper() == "SELECT NAME, OVR FROM PLAYERS LIMIT 3"
        assert result.results == "Top players list"
        assert result.status == "success"
        assert isinstance(result.execution_time, int)
        assert result.raw_rows == [
            {"name": "Messi", "ovr": 93},
            {"name": "Ronaldo", "ovr": 92},
            {"name": "Mbappe", "ovr": 91}
        ]


# ============================================
# Query Endpoint Integration Tests
# ============================================

class TestQueryEndpoint:
    """Tests for /query endpoint."""
    
    @pytest.mark.asyncio
    async def test_returns_success_for_valid_question(self):
        """Test /query endpoint with a valid question."""
        payload = {"question": "Show top 5 players by rating"}
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.post("/query", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "sql_query" in data
        assert data["status"] in ["success", "error"]
    
    @pytest.mark.asyncio
    async def test_returns_full_response_structure(self):
        """Test /query endpoint returns complete response."""
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.post("/query", json={"question": "Show best players"})
        
        assert response.status_code == 200
        data = response.json()
        
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
    async def test_sanitizes_malicious_input(self):
        """Test that malicious input is sanitized into safe SQL."""
        payload = {"question": "DROP TABLE players"}
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.post("/query", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["sql_query"].strip().upper().startswith("SELECT")
        assert data["status"] == "success"

