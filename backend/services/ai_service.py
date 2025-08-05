import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain_experimental.sql.base import SQLDatabaseChain as SQLDatabaseChainType
from .db_service import get_db

# Load environment variables
load_dotenv()
openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

# Create the LLM model
llm: ChatOpenAI = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",
    openai_api_key=openai_api_key
)

# Create SQLDatabaseChain
db_chain: SQLDatabaseChain = SQLDatabaseChain.from_llm(
    llm, get_db(), verbose=True, return_intermediate_steps=True
)

def get_db_chain() -> SQLDatabaseChainType:
    """Return LangChain SQLDatabaseChain instance."""
    return db_chain
