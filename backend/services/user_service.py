# services/user_service.py
import os
from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy import Table, Column, Integer, String, MetaData, TIMESTAMP, select
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from .engine_factory import EngineFactory

load_dotenv()

metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("full_name", String, nullable=False),
    Column("email", String, nullable=False, unique=True),
    Column("password_hash", String, nullable=False),
    Column("created_at", TIMESTAMP, default=datetime.utcnow),
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_engine():
    """Return SQLAlchemy engine instance for users database."""
    # ✅ Pass the environment variable NAME, not the value
    return EngineFactory.get_engine("users_db", "USERS_POSTGRESQL_URL")

def create_user(full_name: str, email: str, password: str):
    engine = get_engine()
    hashed_pw = pwd_context.hash(password)
    with engine.connect() as conn:
        try:
            conn.execute(
                users_table.insert().values(
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

        if not pwd_context.verify(password, user_dict["password_hash"]):
            return None

        return user_dict

def get_user_by_email(email: str):
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            select(users_table).where(users_table.c.email == email)
        ).fetchone()
        return dict(result._mapping) if result else None