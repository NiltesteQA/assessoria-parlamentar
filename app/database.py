"""Configuração do banco de dados (SQLAlchemy + SQLite).

Preparado para migração futura para PostgreSQL: basta alterar
DATABASE_URL (ex.: postgresql+psycopg://user:pass@host/db) e remover
o connect_args específico do SQLite.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SQLITE = f"sqlite:///{os.path.join(BASE_DIR, '..', 'assessoria.db')}"

DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_SQLITE)

# connect_args só é necessário para SQLite (single-thread por padrão).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency do FastAPI que fornece uma sessão por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Cria as tabelas se ainda não existirem."""
    from app import models  # noqa: F401  (garante o registro dos modelos)
    Base.metadata.create_all(bind=engine)
