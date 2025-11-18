from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    history = relationship("History", back_populates="user", cascade="all, delete-orphan")

class History(Base):
    __tablename__ = "history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    sql_query = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # "success" or "error"
    execution_time = Column(Float, nullable=False)  # in milliseconds
    results = Column(Text)  # LLM answer text
    raw_rows = Column(Text)  # JSON string of SQL result rows
    error_message = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="history")