#!/usr/bin/env python3
"""
Initialize test database with players table and sample data.
Used by both pytest (via conftest.py) and E2E tests.

This is the single source of truth for test database initialization.
"""
import os
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String


def create_players_table_and_data(database_url: str = None):
    """
    Create players table with test data.
    
    Args:
        database_url: Database connection URL. If not provided, uses DATABASE_URL env var.
    
    This function is idempotent - it can be called multiple times safely.
    """
    db_url = database_url or os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    engine = create_engine(db_url)
    
    # Define players table schema
    metadata = MetaData()
    players = Table('players', metadata,
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
    )
    
    # Create the table (checkfirst=True makes it idempotent)
    metadata.create_all(engine, checkfirst=True)
    
    # Insert test data (only if table is empty)
    with engine.connect() as conn:
        # Check if data already exists
        result = conn.execute(text("SELECT COUNT(*) FROM players"))
        count = result.scalar()
        
        if count == 0:
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
            print("✅ Inserted 10 test players")
        else:
            print(f"✅ Players table already contains {count} rows, skipping insert")
    
    print("✅ Test database initialized successfully")


if __name__ == "__main__":
    """Run this script directly to initialize the test database."""
    create_players_table_and_data()

