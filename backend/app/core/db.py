from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .settings import settings


class Base(DeclarativeBase):
    pass


def _db_url() -> str:
    storage = Path(settings.storage_dir)
    storage.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{(storage / 'glunova.db').as_posix()}"


engine = create_engine(_db_url(), connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

