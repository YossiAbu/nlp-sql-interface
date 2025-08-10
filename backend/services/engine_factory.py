# services/engine_factory.py
import os
from typing import Dict
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine

load_dotenv()

class EngineFactory:
    """Singleton factory for managing multiple database engines."""
    
    _engines: Dict[str, Engine] = {}
    
    @classmethod
    def get_engine(cls, db_name: str, url_env_var: str) -> Engine:
        """Get or create an engine for a specific database."""
        if db_name not in cls._engines:
            url = os.getenv(url_env_var)
            if not url:
                raise ValueError(f"{url_env_var} is not set")
            cls._engines[db_name] = create_engine(url)
        return cls._engines[db_name]
