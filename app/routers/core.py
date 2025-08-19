from fastapi import APIRouter
from sqlalchemy import text
from app.db import engine

router = APIRouter(tags=["core"])

@router.get("/saude")
def saude():
    return {"status": "ok", "mensagem": "API no ar (Passo 2)!"}

@router.get("/dbinfo")
def dbinfo():
    result = {"schema": engine.url.database, "tables": [], "columns": {}}
    with engine.connect() as conn:
        tables = [row[0] for row in conn.execute(text("SHOW TABLES;"))]
        result["tables"] = tables
        for t in tables:
            rows = conn.execute(text(f"SHOW COLUMNS FROM `{t}`;")).all()
            result["columns"][t] = [
                {
                    "field": r[0],
                    "type": r[1],
                    "nullable": (r[2] == "YES"),
                    "key": r[3],
                    "default": r[4],
                    "extra": r[5],
                }
                for r in rows
            ]
    return result
