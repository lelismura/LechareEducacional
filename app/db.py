# app/db.py
import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carrega o .env da RAIZ do projeto
ROOT_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ROOT_ENV, override=True)

def _req(name: str) -> str:
    v = os.getenv(name)
    if v is None or str(v).strip() == "":
        raise RuntimeError(f"Variável obrigatória ausente: {name} (configure no .env)")
    return str(v)

DB_HOST = _req("DB_HOST")           # ex.: 186.202.152.70  (SEM fallback!)
DB_NAME = _req("DB_NAME")           # ex.: queryanswer
DB_USER = _req("DB_USER")           # ex.: queryanswer
DB_PASS = _req("DB_PASS")           # ex.: Esqueci#25
DB_PORT = int(os.getenv("DB_PORT", "3306"))  # porta pode ter default

# Remove aspas se o .env tiver DB_PASS="algo"
if (DB_PASS.startswith('"') and DB_PASS.endswith('"')) or (DB_PASS.startswith("'") and DB_PASS.endswith("'")):
    DB_PASS = DB_PASS[1:-1]

# Driver: mysql-connector (Oracle) — robusto p/ auth do MySQL 8
URL = f"mysql+mysqlconnector://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "connection_timeout": 10,
        # "allowPublicKeyRetrieval": True,  # descomente se seu provedor exigir
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
