# app/main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.web import router as web_router   # importa as rotas de web.py
from app.routers.flow import router as flow_router
from app.routers.public import router as public_router


app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/start", status_code=307)

# fluxo novo
app.include_router(flow_router)

# APIs
app.include_router(public_router, prefix="/api")

# páginas do web.py (inclui /cartao)
app.include_router(web_router)
