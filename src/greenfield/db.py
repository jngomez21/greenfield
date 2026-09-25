"""Engine, base declarativa y sesión por request."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from greenfield.config import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """Una transacción por request: commit si todo sale bien, rollback si hay excepción."""
    with Session(get_engine()) as session, session.begin():
        yield session
