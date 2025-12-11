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
    from sqlalchemy import Table, Column, Integer, String, Float, MetaData
    
    engine = get_engine()
    
    # Create users and history tables
    metadata.create_all(engine)
    init_db()
    
    # Create players table for integration tests
    test_metadata = MetaData()
    players_table = Table(
        'players',
        test_metadata,
        Column('rank', Integer),
        Column('name', String),
        Column('ovr', Integer),
        Column('position', String),
        Column('team', String),
        Column('nation', String),
        Column('league', String),
        Column('age', Integer),
        Column('height', Integer),
        Column('weight', Integer),
        Column('pac', Integer),
        Column('sho', Integer),
        Column('pas', Integer),
        Column('dri', Integer),
        Column('def', Integer),
        Column('phy', Integer),
        Column('skill_moves', Integer),
        Column('weak_foot', Integer),
        Column('preferred_foot', String),
        Column('sprint_speed', Integer),
        Column('acceleration', Integer),
        Column('finishing', Integer),
        Column('heading_accuracy', Integer),
        Column('vision', Integer),
        Column('ball_control', Integer),
        Column('free_kick_accuracy', Integer),
        Column('gk_diving', Integer),
        Column('gk_handling', Integer),
        Column('gk_kicking', Integer),
        Column('gk_positioning', Integer),
        Column('gk_reflexes', Integer),
        Column('strength', Integer),
        Column('stamina', Integer),
        extend_existing=True
    )
    
    # Create the table
    test_metadata.create_all(engine, checkfirst=True)
    
    # Insert minimal test data (10 diverse players)
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO players (rank, name, ovr, position, team, nation, league, age, height, weight, 
                               pac, sho, pas, dri, def, phy, skill_moves, weak_foot, preferred_foot,
                               sprint_speed, acceleration, finishing, heading_accuracy, vision, ball_control,
                               free_kick_accuracy, gk_diving, gk_handling, gk_kicking, gk_positioning, gk_reflexes,
                               strength, stamina)
            VALUES
                (1, 'Lionel Messi', 93, 'RW', 'Inter Miami', 'Argentina', 'MLS', 36, 170, 72, 85, 92, 91, 95, 35, 65, 4, 4, 'Left', 80, 90, 94, 70, 94, 96, 94, 0, 0, 0, 0, 0, 68, 75),
                (2, 'Cristiano Ronaldo', 91, 'ST', 'Al Nassr', 'Portugal', 'Saudi Pro League', 38, 187, 83, 82, 93, 82, 88, 35, 77, 5, 4, 'Right', 84, 89, 93, 90, 82, 88, 76, 0, 0, 0, 0, 0, 78, 80),
                (3, 'Kevin De Bruyne', 91, 'CM', 'Manchester City', 'Belgium', 'Premier League', 32, 181, 70, 76, 86, 93, 88, 61, 78, 4, 5, 'Right', 78, 80, 85, 82, 94, 90, 87, 0, 0, 0, 0, 0, 75, 88),
                (4, 'Virgil van Dijk', 90, 'CB', 'Liverpool', 'Netherlands', 'Premier League', 32, 193, 92, 77, 60, 70, 72, 92, 86, 1, 3, 'Right', 78, 78, 65, 94, 72, 70, 65, 0, 0, 0, 0, 0, 86, 85),
                (5, 'Kylian Mbappe', 92, 'ST', 'Paris SG', 'France', 'Ligue 1', 24, 178, 73, 97, 89, 80, 92, 36, 77, 5, 4, 'Right', 97, 98, 91, 85, 80, 92, 81, 0, 0, 0, 0, 0, 76, 90),
                (6, 'Marc-Andre ter Stegen', 89, 'GK', 'FC Barcelona', 'Germany', 'La Liga', 31, 187, 85, 50, 40, 68, 55, 45, 70, 1, 3, 'Right', 52, 55, 45, 60, 70, 62, 55, 88, 90, 89, 88, 89, 75, 78),
                (7, 'Vinicius Jr', 90, 'LW', 'Real Madrid', 'Brazil', 'La Liga', 23, 176, 73, 95, 83, 79, 93, 29, 61, 5, 3, 'Right', 95, 96, 88, 55, 78, 94, 77, 0, 0, 0, 0, 0, 68, 82),
                (8, 'Luka Modric', 88, 'CM', 'Real Madrid', 'Croatia', 'La Liga', 38, 172, 66, 74, 73, 91, 90, 72, 65, 4, 4, 'Right', 75, 78, 75, 70, 90, 92, 90, 0, 0, 0, 0, 0, 61, 84),
                (9, 'Erling Haaland', 91, 'ST', 'Manchester City', 'Norway', 'Premier League', 23, 194, 88, 89, 93, 65, 80, 45, 87, 3, 3, 'Left', 90, 92, 95, 85, 68, 82, 65, 0, 0, 0, 0, 0, 88, 89),
                (10, 'Neymar Jr', 89, 'LW', 'Al Hilal', 'Brazil', 'Saudi Pro League', 31, 175, 68, 88, 85, 86, 94, 37, 59, 5, 5, 'Right', 88, 90, 89, 62, 87, 95, 87, 0, 0, 0, 0, 0, 56, 78)
        """))
        conn.commit()


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