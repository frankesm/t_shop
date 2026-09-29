import importlib
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import DB_URL, INSTALLED_APPS

engine = create_engine(DB_URL, echo=False)


@event.listens_for(engine, "connect")
def _activate_fk(dbapi_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)

Base = declarative_base()


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    for app in INSTALLED_APPS:
        importlib.import_module(f"{app}.models")
    Base.metadata.create_all(engine)
