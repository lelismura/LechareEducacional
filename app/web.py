from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/cartao", response_class=HTMLResponse)
async def cartao(request: Request):
    return templates.TemplateResponse("cartao.html", {"request": request})
