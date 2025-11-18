import os
from sqlalchemy import inspect
from .db_service import get_engine
from .logging_service import logger
from models.response_models import SchemaResponse, TableSchema, ColumnSchema

# Cache variable for text schema
SCHEMA_CACHE_TEXT: str | None = None

def get_schema_text(force_refresh: bool = False) -> str:
    """
    Return DB schema as formatted text string for AI prompts.
    Uses cache unless force_refresh=True.
    """
    global SCHEMA_CACHE_TEXT

    if SCHEMA_CACHE_TEXT is None or force_refresh:
        if not os.getenv("DATABASE_URL"):
            raise ValueError("DATABASE_URL is not set")
        logger.info("Fetching database schema (text) from DB...")
        inspector = inspect(get_engine())
        schema_parts = []
        for table_name in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns(table_name)]
            schema_parts.append(f"Table: {table_name} | Columns: {', '.join(columns)}")
        SCHEMA_CACHE_TEXT = "\n".join(schema_parts)

    return SCHEMA_CACHE_TEXT

def get_schema_response(force_refresh: bool = False) -> SchemaResponse:
    """
    Return DB schema as structured JSON for /schema endpoint.
    Always queries DB fresh if force_refresh=True.
    """
    if not os.getenv("DATABASE_URL"):
        raise ValueError("DATABASE_URL is not set")
    if force_refresh:
        logger.info("Refreshing database schema (JSON) from DB...")
    else:
        logger.info("Fetching database schema (JSON) from DB...")
    inspector = inspect(get_engine())
    schema_data = []
    for table_name in inspector.get_table_names():
        columns = [
            ColumnSchema(name=col["name"], type=str(col["type"]))
            for col in inspector.get_columns(table_name)
        ]
        schema_data.append(TableSchema(name=table_name, columns=columns))
    return SchemaResponse(tables=schema_data)

def refresh_schema_cache() -> SchemaResponse:
    """
    Refresh both text and JSON schema caches and return the new JSON schema.
    """
    logger.info("Refreshing both text and JSON schema caches...")
    # Refresh text schema
    get_schema_text(force_refresh=True)
    # Return refreshed JSON schema
    return get_schema_response(force_refresh=True)
