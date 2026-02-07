"""Database engine and session wiring.

SQLite by default (self-contained); set DATABASE_URL to a Postgres DSN to
swap the store without touching application code.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings

settings = get_settings()

# check_same_thread is a SQLite-only flag (needed because FastAPI hands
# sessions across threads); harmless to scope it to sqlite URLs only.
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a scoped session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables. Models must be imported before calling this."""
    from . import models  # noqa: F401  (register mappers)

    Base.metadata.create_all(bind=engine)
