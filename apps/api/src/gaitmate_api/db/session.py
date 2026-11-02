from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from gaitmate_api.config import settings

connect_args = (
    {"options": "-c timezone=UTC"} if settings.database_url.startswith("postgresql") else {}
)
engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def transaction(factory: sessionmaker[Session] = SessionLocal) -> Iterator[Session]:
    """Commit on success and roll back on any exception."""
    with factory.begin() as session:
        yield session


def get_session() -> Iterator[Session]:
    """FastAPI dependency: one transaction for the request or service operation."""
    with transaction() as session:
        yield session
