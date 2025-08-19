from fastapi import APIRouter
from sqlalchemy import text
from app.db import engine

router = APIRouter(tags=["health"])

@router.get("/health/db")
def health_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/health/dbinfo")
def dbinfo():
    try:
        url = engine.url
        host = url.host
        name = url.database
        driver = url.drivername
        with engine.connect() as conn:
            v = conn.execute(text("SELECT @@hostname AS host, @@version AS version, DATABASE() AS db")).mappings().first()
        return {
            "ok": True,
            "driver": driver,
            "configured_host": host,
            "configured_db": name,
            "server_hostname": v.get("host") if v else None,
            "server_version": v.get("version") if v else None,
            "server_current_db": v.get("db") if v else None,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

from fastapi import APIRouter
from sqlalchemy import text
from app.db import engine

router = APIRouter(tags=["health"])

@router.get("/health/url")
def health_url():
    u = engine.url  # não conecta, só lê a URL configurada
    return {"driver": u.drivername, "host": u.host, "db": u.database}

@router.get("/health/db")
def health_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}