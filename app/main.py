# app/main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.web import templates  # mantém o Jinja carregado
from app.routers.flow import router as flow_router      # fluxo novo (/, /start, /quiz, /bye)
from app.routers.public import router as public_router  # suas APIs em /api

app = FastAPI(title="Lechare Educacional")

# arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 1) raiz: manda direto para /start (ganha da tela antiga)
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/start", status_code=307)

# 2) fluxo novo (start/quiz/bye)
app.include_router(flow_router)

# 3) APIs existentes
app.include_router(public_router, prefix="/api")
