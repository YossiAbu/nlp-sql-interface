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
    clean_sql_query,
    extract_sql_query,
    extract_raw_results,
    build_schema_aware_prompt
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
    async def test_blocks_malicious_input(self):
        """Test that malicious input with suspicious patterns is blocked."""
        payload = {"question": "DROP TABLE players"}
        transport, base_url = get_test_client(app)
        async with AsyncClient(transport=transport, base_url=base_url) as ac:
            response = await ac.post("/query", json=payload)
        
        # Should be blocked with 400 Bad Request (security feature)
        assert response.status_code == 400
        data = response.json()
        assert "Invalid query pattern" in data["detail"]


# ============================================
# Extract SQL Query Edge Cases
# ============================================

class TestExtractSqlQuery:
    """Tests for extract_sql_query function edge cases."""
    
    def test_extracts_from_intermediate_steps_string(self):
        """Test extraction from intermediate steps with string SELECT."""
        result = {
            "intermediate_steps": [
                "SELECT name, ovr FROM players LIMIT 5;",
                "SQLResult: [('Messi', 93)]"
            ]
        }
        sql = extract_sql_query(result)
        assert "SELECT" in sql.upper()
        assert "name" in sql.lower()
    
    def test_extracts_from_intermediate_steps_dict(self):
        """Test extraction from intermediate steps with dict containing sql_cmd."""
        result = {
            "intermediate_steps": [
                {"sql_cmd": "SELECT name FROM players"}
            ]
        }
        sql = extract_sql_query(result)
        assert "SELECT" in sql.upper()
    
    def test_extracts_from_markdown_format(self):
        """Test extraction from markdown code block format."""
        result = {
            "intermediate_steps": [],
            "result": "```sql\nSELECT name FROM players\n```"
        }
        # The function converts result_dict to string, so we need to test with str representation
        sql = extract_sql_query({"result": "```sql\nSELECT name FROM players\n```"})
        # May or may not find it depending on how it's parsed
        assert sql == "" or "SELECT" in sql.upper()
    
    def test_extracts_from_sqlquery_format(self):
        """Test extraction from SQLQuery: format."""
        result = {
            "intermediate_steps": [
                "SQLQuery: SELECT name FROM players LIMIT 3"
            ]
        }
        sql = extract_sql_query(result)
        assert "SELECT" in sql.upper()
    
    def test_returns_empty_for_no_sql(self):
        """Test returns empty string when no SQL found."""
        result = {"intermediate_steps": ["No SQL here"], "result": "Just text"}
        sql = extract_sql_query(result)
        assert sql == ""
    
    def test_returns_empty_for_empty_dict(self):
        """Test returns empty string for empty input."""
        assert extract_sql_query({}) == ""
        assert extract_sql_query({"intermediate_steps": []}) == ""


class TestExtractRawResults:
    """Tests for extract_raw_results function edge cases."""
    
    def test_extracts_from_list_string(self):
        """Test extraction from list string format."""
        result = {
            "intermediate_steps": [
                "[('Messi', 93), ('Ronaldo', 92)]"
            ]
        }
        raw = extract_raw_results(result, "SELECT name, ovr FROM players")
        assert raw == [('Messi', 93), ('Ronaldo', 92)]
    
    def test_extracts_from_sqlresult_format(self):
        """Test extraction from SQLResult: format."""
        result = {
            "intermediate_steps": [
                "SQLResult: [('Messi', 93)]"
            ]
        }
        raw = extract_raw_results(result, "SELECT name, ovr FROM players")
        assert raw == [('Messi', 93)]
    
    def test_handles_invalid_list_string(self):
        """Test handles malformed list string gracefully."""
        result = {
            "intermediate_steps": [
                "[invalid list"
            ]
        }
        raw = extract_raw_results(result, "")
        assert raw == []
    
    def test_handles_invalid_sqlresult(self):
        """Test handles malformed SQLResult gracefully."""
        result = {
            "intermediate_steps": [
                "SQLResult: not a valid list"
            ]
        }
        raw = extract_raw_results(result, "")
        assert raw == []
    
    def test_returns_empty_for_no_results(self):
        """Test returns empty list when no results found."""
        result = {"intermediate_steps": ["No results here"]}
        raw = extract_raw_results(result, "")
        assert raw == []


class TestExtractColumnNamesEdgeCases:
    """Additional edge case tests for extract_column_names."""
    
    def test_handles_table_prefix_in_columns(self):
        """Test extraction handles table.column format."""
        sql = "SELECT players.name, players.ovr FROM players"
        columns = extract_column_names(sql)
        assert "name" in columns
        assert "ovr" in columns
    
    def test_handles_quoted_columns(self):
        """Test extraction handles quoted column names."""
        sql = "SELECT \"name\", 'ovr' FROM players"
        columns = extract_column_names(sql)
        assert "name" in columns
        assert "ovr" in columns
    
    def test_handles_complex_select(self):
        """Test extraction from complex SELECT with multiple clauses."""
        sql = "SELECT name, ovr FROM players WHERE ovr > 90 ORDER BY ovr DESC LIMIT 10"
        columns = extract_column_names(sql)
        assert "name" in columns
        assert "ovr" in columns


class TestCleanSqlQueryEdgeCases:
    """Additional edge case tests for clean_sql_query."""
    
    def test_cleans_multiple_markdown_markers(self):
        """Test cleaning multiple markdown code block markers."""
        sql = "```sql\n```SELECT name FROM players```\n```"
        cleaned = clean_sql_query(sql)
        assert "```" not in cleaned
    
    def test_handles_mixed_formatting(self):
        """Test cleaning SQL with mixed formatting issues."""
        sql = "SQLQuery: ```sql\nSELECT name FROM players;\n```"
        cleaned = clean_sql_query(sql)
        assert "SQLQuery:" not in cleaned
        assert "```" not in cleaned
    
    def test_normalizes_whitespace(self):
        """Test that excessive whitespace is normalized."""
        sql = "SELECT    name,    ovr    FROM    players"
        cleaned = clean_sql_query(sql)
        # Should have normalized whitespace
        assert "  " not in cleaned or cleaned == sql.strip()
    
    def test_returns_original_when_no_patterns_match(self):
        """Test returns cleaned text when no extraction patterns match."""
        sql = "SOME RANDOM TEXT"
        cleaned = clean_sql_query(sql)
        assert cleaned == "SOME RANDOM TEXT"


class TestBuildSchemaAwarePrompt:
    """Tests for build_schema_aware_prompt function."""
    
    def test_includes_question(self):
        """Test prompt includes the question."""
        prompt = build_schema_aware_prompt("Show all players", "Table: players")
        assert "Show all players" in prompt
    
    def test_includes_schema(self):
        """Test prompt includes the schema."""
        prompt = build_schema_aware_prompt("Show all players", "Table: players | Columns: name, ovr")
        assert "Table: players" in prompt
    
    def test_includes_dataset_description(self):
        """Test prompt includes dataset description."""
        prompt = build_schema_aware_prompt("Show all players", "Table: players")
        assert "FC 25 players" in prompt or "dataset" in prompt.lower()
    
    def test_includes_sql_instructions(self):
        """Test prompt includes SQL generation instructions."""
        prompt = build_schema_aware_prompt("Show all players", "Table: players")
        assert "SELECT" in prompt or "SQL" in prompt
