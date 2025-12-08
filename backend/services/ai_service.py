import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from .db_service import get_db
from .logging_service import logger


load_dotenv()

openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

_llm: ChatOpenAI | None = None
_db_chain: SQLDatabaseChain | None = None
_current_model: str | None = os.getenv("OPENAI_MODEL")  # add global

def get_db_chain() -> SQLDatabaseChain:
    """Return LangChain SQLDatabaseChain instance, creating it if necessary."""
    global _llm, _db_chain, _current_model

    if _db_chain is None:
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        if _llm is None:
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # allow override via .env
            _current_model = model_name
            _llm = ChatOpenAI(
                temperature=0,
                model=model_name,
                openai_api_key=openai_api_key
            )
        _db_chain = SQLDatabaseChain.from_llm(
            _llm, get_db(), verbose=True, return_intermediate_steps=True
        )

    return _db_chain


def get_current_model() -> str:
    return _current_model or "unknown"
