import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from .db_service import get_db

load_dotenv()

openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

_llm: ChatOpenAI | None = None
_db_chain: SQLDatabaseChain | None = None

def get_db_chain() -> SQLDatabaseChain:
    """Return LangChain SQLDatabaseChain instance, creating it if necessary."""
    global _llm, _db_chain

    if _db_chain is None:
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        if _llm is None:
            _llm = ChatOpenAI(
                temperature=0,
                model="gpt-3.5-turbo",
                openai_api_key=openai_api_key
            )
        _db_chain = SQLDatabaseChain.from_llm(
            _llm, get_db(), verbose=True, return_intermediate_steps=True
        )

    return _db_chain
