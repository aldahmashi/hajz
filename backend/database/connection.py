"""SQLAlchemy engines and sessions (read-write and read-only), RMC style.

Difference from RMC: the read-write session is NOT committed automatically at
the end of the request. Services commit explicitly with `transaction()`, so a
failed commit raises before the response is built and the client never sees a
false success. Anything left uncommitted is rolled back on teardown.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from flask import Flask, g, has_request_context, request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

_WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class Base(DeclarativeBase):
    pass


engine: Engine | None = None
engine_ro: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None
SessionLocalRO: sessionmaker[Session] | None = None


def connect_args(ssl_ca: str) -> dict:
    """TLS with certificate verification when a CA bundle is configured (TiDB Cloud)."""
    if not ssl_ca:
        return {}
    return {"ssl": {"ca": ssl_ca, "check_hostname": True}}


def _engine(url: str, ssl_ca: str, echo: bool = False) -> Engine:
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=1800,
        pool_timeout=10,
        echo=echo,
        connect_args=connect_args(ssl_ca),
    )


def init_db(app: Flask) -> None:
    global engine, engine_ro, SessionLocal, SessionLocalRO

    ssl_ca = app.config.get("DB_SSL_CA", "")
    engine = _engine(app.config["DATABASE_URL"], ssl_ca)
    engine_ro = _engine(app.config["DATABASE_URL_RO"], ssl_ca)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    SessionLocalRO = sessionmaker(bind=engine_ro, autoflush=False, expire_on_commit=False)


def get_write_session() -> Session:
    if SessionLocal is None:
        raise RuntimeError("Database has not been initialized")
    if not has_request_context():
        return SessionLocal()
    if "db_session" not in g:
        g.db_session = SessionLocal()
    return g.db_session


def get_ro_session() -> Session:
    if SessionLocalRO is None:
        raise RuntimeError("Database has not been initialized")
    if not has_request_context():
        return SessionLocalRO()
    if "db_ro_session" not in g:
        g.db_ro_session = SessionLocalRO()
    return g.db_ro_session


def get_session() -> Session:
    """GET/HEAD/OPTIONS use the read-only session, writes use the read-write session."""
    if has_request_context() and request.method in _WRITE_METHODS:
        return get_write_session()
    return get_ro_session()


@contextmanager
def transaction() -> Iterator[Session]:
    """Explicit write transaction: commit on success, roll back on any error."""
    session = get_write_session()
    if session.in_transaction() and session.info.get("in_explicit_transaction"):
        yield session
        return

    session.info["in_explicit_transaction"] = True
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.info.pop("in_explicit_transaction", None)


def close_sessions(exception: BaseException | None = None) -> None:
    for key in ("db_session", "db_ro_session"):
        session = g.pop(key, None)
        if session is None:
            continue
        try:
            session.rollback()
        finally:
            session.close()
