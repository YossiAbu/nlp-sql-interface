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

    # Mock AI chain
    def fake_get_db_chain():
        return FakeDBChain()
    monkeypatch.setattr(qs, "get_db_chain", fake_get_db_chain)

    # Mock schema text
    monkeypatch.setattr(ss, "get_schema_text", lambda force_refresh=False: "Table: players | Columns: name, ovr")
    monkeypatch.setattr(qs, "get_schema_text", lambda force_refresh=False: "Table: players | Columns: name, ovr")

    # Mock schema endpoints so no DB is needed
    monkeypatch.setattr(ss, "get_schema_response", lambda force_refresh=False: {"tables": []})
    monkeypatch.setattr(ss, "refresh_schema_cache", lambda: {"tables": []})
