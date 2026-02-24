import os
from dotenv import load_dotenv
from openai import OpenAI
from .logging_service import logger

load_dotenv()

_client: OpenAI | None = None
_current_model: str | None = os.getenv("OPENAI_MODEL")

def get_client() -> OpenAI:
    """Return OpenAI client singleton."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        _client = OpenAI(api_key=api_key)
    return _client

def get_current_model() -> str:
    return _current_model or "gpt-4o-mini"

def generate_sql(system_prompt: str, user_question: str) -> str:
    """Generate SQL from natural language using OpenAI chat completions."""
    global _current_model
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    _current_model = model

    client = get_client()
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question},
        ],
    )
    return response.choices[0].message.content or ""
