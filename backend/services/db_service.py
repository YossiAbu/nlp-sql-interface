# services/db_service.py
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, Session
from .engine_factory import EngineFactory
from models.history import Base

load_dotenv()

_session_maker = None

def get_engine():
    """Return SQLAlchemy engine instance for main database."""
    return EngineFactory.get_engine("main_db", "DATABASE_URL")

def get_session_maker():
    """Return sessionmaker for ORM operations."""
    global _session_maker
    if _session_maker is None:
        engine = get_engine()
        _session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _session_maker

def get_session() -> Session:
    """Create and return a new database session."""
    SessionLocal = get_session_maker()
    return SessionLocal()

def init_db():
    """Initialize database tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

def execute_raw_sql(sql_query: str) -> list[tuple]:
    """Execute a raw SQL query and return rows as list of tuples."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        return [tuple(row) for row in result.fetchall()]
