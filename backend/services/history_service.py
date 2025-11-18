from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from models.history import History
from schemas.history import HistoryCreate, HistoryResponse, HistoryListResponse
import json
from typing import Optional, List, Dict, Any

class HistoryService:
    
    @staticmethod
    def create_history_entry(
        db: Session, 
        user_id: str, 
        history_data: HistoryCreate
    ) -> HistoryResponse:
        """Create a new history entry"""
        # Convert raw_rows to JSON string for storage
        raw_rows_json = json.dumps(history_data.raw_rows) if history_data.raw_rows else None
        
        db_history = History(
            user_id=user_id,
            question=history_data.question,
            sql_query=history_data.sql_query,
            status=history_data.status,
            execution_time=history_data.execution_time,
            results=history_data.results,
            raw_rows=raw_rows_json,
            error_message=history_data.error_message
        )
        
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        
        return HistoryService._to_response(db_history)
    
    @staticmethod
    def get_user_history(
        db: Session, 
        user_id: str, 
        page: int = 1, 
        per_page: int = 20
    ) -> HistoryListResponse:
        """Get paginated history for a user"""
        offset = (page - 1) * per_page
        
        # Get total count
        total = db.query(func.count(History.id)).filter(History.user_id == user_id).scalar()
        
        # Get paginated results
        histories = (
            db.query(History)
            .filter(History.user_id == user_id)
            .order_by(desc(History.created_date))
            .offset(offset)
            .limit(per_page)
            .all()
        )
        
        total_pages = (total + per_page - 1) // per_page
        
        return HistoryListResponse(
            items=[HistoryService._to_response(h) for h in histories],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    
    @staticmethod
    def get_history_by_id(db: Session, history_id: str, user_id: str) -> Optional[HistoryResponse]:
        """Get a specific history entry"""
        history = (
            db.query(History)
            .filter(History.id == history_id, History.user_id == user_id)
            .first()
        )
        
        return HistoryService._to_response(history) if history else None
    
    @staticmethod
    def delete_history_entry(db: Session, history_id: str, user_id: str) -> bool:
        """Delete a specific history entry"""
        deleted = (
            db.query(History)
            .filter(History.id == history_id, History.user_id == user_id)
            .delete()
        )
        db.commit()
        return deleted > 0
    
    @staticmethod
    def clear_user_history(db: Session, user_id: str) -> int:
        """Clear all history for a user"""
        deleted = db.query(History).filter(History.user_id == user_id).delete()
        db.commit()
        return deleted
    
    @staticmethod
    def _to_response(history: History) -> HistoryResponse:
        """Convert DB model to response schema"""
        raw_rows = json.loads(history.raw_rows) if history.raw_rows else None
        
        return HistoryResponse(
            id=history.id,
            user_id=history.user_id,
            question=history.question,
            sql_query=history.sql_query,
            status=history.status,
            execution_time=history.execution_time,
            results=history.results,
            raw_rows=raw_rows,
            error_message=history.error_message,
            created_date=history.created_date
        )