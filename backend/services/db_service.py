import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain.utilities import SQLDatabase

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
postgres_url = os.getenv("POSTGRESQL_URL")

# Create SQLAlchemy engine
engine = create_engine(postgres_url)

# LangChain SQLDatabase object
db = SQLDatabase.from_uri(postgres_url)

def get_engine():
    return engine

def get_db():
    return db
