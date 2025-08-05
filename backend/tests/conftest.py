import pytest
from typing import Any, Dict

class FakeDBChain:
    """Fake AI chain that always returns the same SQL and result."""
    def invoke(self, prompt: str) -> Dict[str, Any]:
        return {
            "result": "Top players list",
            "intermediate_steps": [
                "SELECT name, ovr FROM players LIMIT 3;",
                "SQLResult: [('Messi', 93), ('Ronaldo', 92), ('Mbappe', 91)]"
            ]
        }

@pytest.fixture(autouse=True)
def mock_services(monkeypatch):
    """Automatically mock AI chain and schema for all tests."""
    import services.query_service as qs
    import services.schema_service as ss
    import main

    # ---- Mock AI chain ----
    def fake_get_db_chain():
        return FakeDBChain()
    monkeypatch.setattr(qs, "get_db_chain", fake_get_db_chain)

    # ---- Fake schema data ----
    fake_schema_text = "Table: players | Columns: name, ovr"
    fake_schema_json = {
        "tables": [
            {
                "name": "players",
                "columns": [
                    {"name": "name", "type": "text"},
                    {"name": "ovr", "type": "integer"}
                ]
            }
        ]
    }

    # Patch schema text
    monkeypatch.setattr(ss, "get_schema_text", lambda force_refresh=False: fake_schema_text)
    monkeypatch.setattr(qs, "get_schema_text", lambda force_refresh=False: fake_schema_text)

    # Patch schema response
    monkeypatch.setattr(ss, "get_schema_response", lambda force_refresh=False: fake_schema_json)
    monkeypatch.setattr(main, "get_schema_response", lambda force_refresh=False: fake_schema_json)

    # Patch refresh schema cache
    monkeypatch.setattr(ss, "refresh_schema_cache", lambda: fake_schema_json)
    monkeypatch.setattr(main, "refresh_schema_cache", lambda: fake_schema_json)
