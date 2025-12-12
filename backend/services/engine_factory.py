# services/engine_factory.py
import os
from typing import Dict
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import QueuePool

load_dotenv()

class EngineFactory:
    """Singleton factory for managing multiple database engines with connection pooling."""
    
    _engines: Dict[str, Engine] = {}
    
    @classmethod
    def get_engine(cls, db_name: str, url_env_var: str) -> Engine:
        """
        Get or create an engine for a specific database with optimized connection pooling.
        
        Connection Pool Configuration:
        - pool_size: 5 connections maintained in the pool
        - max_overflow: 10 additional connections can be created when needed
        - pool_pre_ping: Verifies connections before use (handles stale connections)
        - pool_recycle: Recycles connections after 1 hour (prevents timeout issues)
        """
        if db_name not in cls._engines:
            url = os.getenv(url_env_var)
            if not url:
                raise ValueError(f"{url_env_var} is not set")
            
            cls._engines[db_name] = create_engine(
                url,
                poolclass=QueuePool,
                pool_size=5,              # Number of connections to keep in pool
                max_overflow=10,          # Max additional connections beyond pool_size
                pool_pre_ping=True,       # Verify connection health before using
                pool_recycle=3600,        # Recycle connections after 1 hour
                echo=False,               # Set to True for SQL debugging
            )
        return cls._engines[db_name]
