"""Database connection setup.

The engine is the connection to the database file, a session is one
"conversation" with the database, and get_db() gives every API request
its own session and closes it when the request is finished.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# SQLite stores the whole database in one file called grocery.db.
# To use PostgreSQL later, set DATABASE_URL in the environment instead.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./grocery.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Every table class inherits from this."""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
