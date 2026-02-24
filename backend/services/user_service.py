# services/user_service.py
import os
import uuid
from datetime import datetime
import bcrypt
from sqlalchemy import Table, Column, String, MetaData, TIMESTAMP, select
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from .engine_factory import EngineFactory

load_dotenv()

metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("full_name", String, nullable=False),
    Column("email", String, nullable=False, unique=True),
    Column("password_hash", String, nullable=False),
    Column("created_at", TIMESTAMP, default=datetime.utcnow),
)

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def get_engine():
    """Return SQLAlchemy engine instance for users database."""
    return EngineFactory.get_engine("nlp_sql_db", "DATABASE_URL")

def create_user(full_name: str, email: str, password: str):
    engine = get_engine()
    hashed_pw = _hash_password(password)
    user_id = str(uuid.uuid4())
    with engine.connect() as conn:
        try:
            conn.execute(
                users_table.insert().values(
                    id=user_id,
                    full_name=full_name,
                    email=email,
                    password_hash=hashed_pw
                )
            )
            conn.commit()
            return True
        except IntegrityError:
            return False

def authenticate_user(email: str, password: str):
    engine = get_engine()
    with engine.connect() as conn:
        user = conn.execute(
            select(users_table).where(users_table.c.email == email)
        ).fetchone()

        if not user:
            return None

        user_dict = dict(user._mapping)

        if not _verify_password(password, user_dict["password_hash"]):
            return None

        return user_dict

def get_user_by_email(email: str):
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            select(users_table).where(users_table.c.email == email)
        ).fetchone()
        return dict(result._mapping) if result else None

def get_user_by_id(user_id: str):
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            select(users_table).where(users_table.c.id == user_id)
        ).fetchone()
        return dict(result._mapping) if result else None