from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime

class HistoryBase(BaseModel):
    question: str
    sql_query: str
    status: str
    execution_time: float
    results: Optional[str] = None
    error_message: Optional[str] = None

class HistoryCreate(HistoryBase):
    raw_rows: Optional[List[Dict[str, Any]]] = None

class HistoryResponse(HistoryBase):
    id: str
    user_id: str
    raw_rows: Optional[List[Dict[str, Any]]] = None
    created_date: datetime
    
    class Config:
        from_attributes = True

class HistoryListResponse(BaseModel):
    items: List[HistoryResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class RerunQueryRequest(BaseModel):
    history_id: str