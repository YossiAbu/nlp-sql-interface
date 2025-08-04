from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryResponse(BaseModel):
    sql_query: str
    results: str
    raw_rows: List[Dict[str, Any]]
    status: str
    execution_time: int
    error_message: Optional[str] = None

class ColumnSchema(BaseModel):
    name: str
    type: str

class TableSchema(BaseModel):
    name: str
    columns: List[ColumnSchema]

class SchemaResponse(BaseModel):
    tables: List[TableSchema]
