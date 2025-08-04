from sqlalchemy import inspect
from .db_service import get_engine
from .logging_service import logger
from models.response_models import SchemaResponse, TableSchema, ColumnSchema

SCHEMA_CACHE = None

def get_schema_text(force_refresh: bool = False) -> str:
    """Return DB schema as text (cached)."""
    global SCHEMA_CACHE
    if SCHEMA_CACHE is None or force_refresh:
        logger.info("Fetching database schema from DB...")
        inspector = inspect(get_engine())
        schema_parts = []
        for table_name in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns(table_name)]
            schema_parts.append(f"Table: {table_name} | Columns: {', '.join(columns)}")
        SCHEMA_CACHE = "\n".join(schema_parts)
    return SCHEMA_CACHE

def get_schema_response() -> SchemaResponse:
    """Return schema as structured Pydantic response."""
    inspector = inspect(get_engine())
    schema_data = []
    for table_name in inspector.get_table_names():
        columns = [ColumnSchema(name=col["name"], type=str(col["type"]))
                   for col in inspector.get_columns(table_name)]
        schema_data.append(TableSchema(name=table_name, columns=columns))
    return SchemaResponse(tables=schema_data)
