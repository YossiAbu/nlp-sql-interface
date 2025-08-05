import os
from typing import Any
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from langchain.utilities import SQLDatabase

# Load environment variables
load_dotenv()
openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
postgres_url: str | None = os.getenv("POSTGRESQL_URL")

# Create SQLAlchemy engine
engine: Engine = create_engine(postgres_url)

# LangChain SQLDatabase object
db: SQLDatabase = SQLDatabase.from_uri(postgres_url)

def get_engine() -> Engine:
    """Return SQLAlchemy engine instance."""
    return engine

def get_db() -> SQLDatabase:
    """Return LangChain SQLDatabase instance."""
    return db
