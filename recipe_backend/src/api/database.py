import os
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

DEFAULT_DB_URL = "sqlite:///./recipes.db"


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


def _get_db_url() -> str:
    """
    Resolve database URL from environment. Defaults to sqlite file in project root.
    Honors DB_URL env var.
    """
    db_url = os.getenv("DB_URL", DEFAULT_DB_URL)
    # For SQLite, ensure correct connect args
    return db_url


def _create_engine_for_url(db_url: str):
    """Create SQLAlchemy engine with appropriate connect args for SQLite."""
    connect_args = {}
    if db_url.startswith("sqlite"):
        # Needed to allow SQLite usage across threads with FastAPI
        connect_args = {"check_same_thread": False}
    return create_engine(db_url, connect_args=connect_args)


DB_URL = _get_db_url()
engine = _create_engine_for_url(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """Yield a database session for request scope and handle cleanup."""
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()


# PUBLIC_INTERFACE
def init_db() -> None:
    """Create all database tables if they do not exist."""
    # Lazy import to avoid circular import with models
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
