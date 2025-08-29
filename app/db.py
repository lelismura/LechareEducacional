import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Verifique se a aplicação está em ambiente de nuvem
if not os.getenv("K_SERVICE"):
    # Carrega o .env da RAIZ do projeto, apenas se não for no Cloud Run
    ROOT_ENV = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=ROOT_ENV, override=True)

def _req(name: str) -> str:
    v = os.getenv(name)
    if v is None or str(v).strip() == "":
        raise RuntimeError(f"Variável obrigatória ausente: {name} (configure no .env)")
    return str(v)

DB_HOST = _req("DB_HOST")
DB_NAME = _req("DB_NAME")
DB_USER = _req("DB_USER")
DB_PASS = _req("DB_PASS")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

if (DB_PASS.startswith('"') and DB_PASS.endswith('"')) or (DB_PASS.startswith("'") and DB_PASS.endswith("'")):
    DB_PASS = DB_PASS[1:-1]

URL = f"mysql+mysqlconnector://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "connection_timeout": 10,
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