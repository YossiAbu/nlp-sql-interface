# backend/tests/conftest.py
import os
import pytest
from typing import Any, Dict
from dotenv import load_dotenv


# ============================================
# Load Test Environment Variables
# ============================================
test_env_path = os.path.join(os.path.dirname(__file__), '..', '.env.test')
if os.path.exists(test_env_path):
    load_dotenv(test_env_path, override=True)


# ============================================
# Initialize Database Tables Before Tests
# ============================================
def pytest_sessionstart(session):
    """Create all database tables before any tests run."""
    from services.db_service import init_db
    from services.user_service import users_table, metadata, get_engine
    
    engine = get_engine()
    metadata.create_all(engine)
    init_db()


# ============================================
# Register Custom Pytest Markers
# ============================================
def pytest_configure(config):
    """Register custom markers to avoid warnings."""
    config.addinivalue_line(
        "markers", "no_mock: Skip automatic mocking fixtures for real database tests"
    )
    config.addinivalue_line(
        "markers", "real_db: Tests that require a populated real database (skipped in CI)"
    )


# ============================================
# Auto-Skip Real DB Tests in CI
# ============================================
def pytest_collection_modifyitems(config, items):
    """Automatically skip real_db tests when running in CI."""
    if os.getenv("CI") == "true":
        skip_ci = pytest.mark.skip(reason="Skipping real DB test in CI - requires populated database")
        for item in items:
            if "real_db" in item.keywords:
                item.add_marker(skip_ci)


# ============================================
# Mock Services Fixture
# ============================================
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
def mock_services(request, monkeypatch):
    """Automatically mock AI chain and schema for all tests."""
    
    if 'no_mock' in request.keywords:
        return  # Skip mocking for tests marked with @pytest.mark.no_mock

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