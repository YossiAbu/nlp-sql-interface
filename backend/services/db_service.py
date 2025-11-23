# services/db_service.py
import os
from dotenv import load_dotenv
from langchain.utilities import SQLDatabase
from sqlalchemy.orm import sessionmaker, Session
from .engine_factory import EngineFactory
from models.history import Base

load_dotenv()

openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

_db: SQLDatabase | None = None
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

def get_db() -> SQLDatabase:
    """Return LangChain SQLDatabase instance."""
    global _db
    if _db is None:
        postgres_url = os.getenv("DATABASE_URL")
        if not postgres_url:
            raise ValueError("DATABASE_URL is not set")
        _db = SQLDatabase.from_uri(postgres_url)
    return _db