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
def mock_get_db_chain(monkeypatch):
    """Automatically mock get_db_chain in all tests."""
    from services import query_service

    def fake_get_db_chain():
        return FakeDBChain()

    monkeypatch.setattr(query_service, "get_db_chain", fake_get_db_chain)
