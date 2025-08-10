# services/db_service.py
import os
from dotenv import load_dotenv
from langchain.utilities import SQLDatabase
from .engine_factory import EngineFactory

load_dotenv()

openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

_db: SQLDatabase | None = None

def get_engine():
    """Return SQLAlchemy engine instance for main database."""
    # ✅ Pass the environment variable NAME, not the value
    return EngineFactory.get_engine("main_db", "FC25_POSTGRESQL_URL")

def get_db() -> SQLDatabase:
    """Return LangChain SQLDatabase instance."""
    global _db
    if _db is None:
        postgres_url = os.getenv("FC25_POSTGRESQL_URL")
        if not postgres_url:
            raise ValueError("FC25_POSTGRESQL_URL is not set")
        _db = SQLDatabase.from_uri(postgres_url)
    return _db