import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from langchain.utilities import SQLDatabase

load_dotenv()

openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
postgres_url: str | None = os.getenv("FC25_POSTGRESQL_URL")

_engine: Engine | None = None
_db: SQLDatabase | None = None

def get_engine() -> Engine:
    """Return SQLAlchemy engine instance."""
    global _engine
    if _engine is None:
        if not postgres_url:
            raise ValueError("POSTGRESQL_URL is not set")
        _engine = create_engine(postgres_url)
    return _engine

def get_db() -> SQLDatabase:
    """Return LangChain SQLDatabase instance."""
    global _db
    if _db is None:
        if not postgres_url:
            raise ValueError("POSTGRESQL_URL is not set")
        _db = SQLDatabase.from_uri(postgres_url)
    return _db
