from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from app.db import engine

# --- defina primeiro templates e router (antes dos @decorators!) ---
templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["auth"])

# cookies da disciplina
DISC_ID_COOKIE = "educapp_disc_id"
DISC_NAME_COOKIE = "educapp_disc_name"

# --------- /access: escolher disciplina + senha ---------
@router.get("/access", response_class=HTMLResponse)
def get_access(request: Request):
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id_discipline, no_discipline FROM tbl_discipline ORDER BY no_discipline")
        ).all()
    disciplinas = [dict(r._mapping) for r in rows]
    return templates.TemplateResponse(
        "auth_access.html",
        {"request": request, "titulo": "Escolher disciplina • Lechare",
         "disciplinas": disciplinas, "error": None}
    )

@router.post("/access")
def post_access(
    request: Request,
    discipline_id: int = Form(...),
    discipline_pwd: str = Form(...),
):
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT id_discipline, no_discipline, pw_password
                FROM tbl_discipline WHERE id_discipline = :i
            """),
            {"i": discipline_id},
        ).fetchone()

    if (not row) or (str(row.pw_password) != str(discipline_pwd)):
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT id_discipline, no_discipline FROM tbl_discipline ORDER BY no_discipline")
            ).all()
        disciplinas = [dict(r._mapping) for r in rows]
        return templates.TemplateResponse(
            "auth_access.html",
            {"request": request, "titulo": "Escolher disciplina • Lechare",
             "disciplinas": disciplinas, "error": "Senha da disciplina incorreta."},
            status_code=400
        )

    resp = RedirectResponse(url="/login", status_code=303)
    resp.set_cookie(DISC_ID_COOKIE, str(row.id_discipline), max_age=60*60*6, httponly=True, samesite="lax")
    resp.set_cookie(DISC_NAME_COOKIE, str(row.no_discipline), max_age=60*60*6, httponly=False, samesite="lax")
    return resp

# --------- /login ---------
@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    disc_id = request.cookies.get(DISC_ID_COOKIE)
    if not disc_id:
        return RedirectResponse(url="/access", status_code=303)

    disc_name = request.cookies.get(DISC_NAME_COOKIE)
    if not disc_name:
        with engine.connect() as conn:
            r = conn.execute(
                text("SELECT no_discipline FROM tbl_discipline WHERE id_discipline = :i"),
                {"i": disc_id},
            ).fetchone()
            disc_name = r.no_discipline if r else ""

    qp = request.query_params
    notice = "Conta criada com sucesso. Faça login." if qp.get("created") == "1" else None
    username = qp.get("username", "")

    return templates.TemplateResponse(
        "auth_login.html",
        {"request": request, "titulo": "Entrar • Lechare Educacional",
         "error": None, "notice": notice, "username": username,
         "disciplina": {"id": disc_id, "name": disc_name} if disc_name else None}
    )

@router.post("/login")
def post_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    disc_id = request.cookies.get(DISC_ID_COOKIE)
    disc_name = request.cookies.get(DISC_NAME_COOKIE, "")
    if not disc_id:
        return RedirectResponse(url="/access", status_code=303)

    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id_usr, no_name, pw_password, ds_type FROM tbl_usr WHERE no_name = :u LIMIT 1"),
            {"u": username},
        ).fetchone()

    if not row or str(row.pw_password) != str(password):
        return templates.TemplateResponse(
            "auth_login.html",
            {"request": request, "titulo": "Entrar • Lechare Educacional",
             "error": "Credenciais inválidas.", "notice": None, "username": username,
             "disciplina": {"id": disc_id, "name": disc_name}},
            status_code=400
        )

    # --- reconhecimento robusto de admin ---
    ds = str(row.ds_type or "").strip()
    ds_l = ds.lower()
    is_admin = (
        ds_l in {"admin", "adm", "administrator", "administrador"}      # valores comuns
        or (ds != "" and not ds.isdigit())                               # qualquer valor não numérico e não vazio
        or row.no_name.strip().lower() == "admin"                        # usuário chamado "admin"
    )

    # se NÃO for admin, precisa pertencer à disciplina escolhida (ds_type = id_discipline)
    if (not is_admin) and (str(row.ds_type or "") != str(disc_id)):
        return templates.TemplateResponse(
            "auth_login.html",
            {"request": request, "titulo": "Entrar • Lechare Educacional",
             "error": "Usuário não pertence a esta disciplina.",
             "notice": None, "username": username,
             "disciplina": {"id": disc_id, "name": disc_name}},
            status_code=400
        )

    # login OK
    max_age = 60*60*24*30 if remember else 60*60*4
    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie("educapp_user", value=str(row.no_name), max_age=max_age, httponly=True, samesite="lax")
    resp.set_cookie("educapp_type", value=("admin" if is_admin else "comum"), max_age=max_age, httponly=True, samesite="lax")
    resp.set_cookie(DISC_ID_COOKIE, str(disc_id), max_age=max_age, httponly=True, samesite="lax")
    resp.set_cookie(DISC_NAME_COOKIE, str(disc_name), max_age=max_age, httponly=False, samesite="lax")
    return resp

# --------- /signup ---------
@router.get("/signup", response_class=HTMLResponse)
def get_signup(request: Request):
    disc_id = request.cookies.get(DISC_ID_COOKIE)
    disc_name = request.cookies.get(DISC_NAME_COOKIE)
    if not disc_id:
        return RedirectResponse(url="/access", status_code=303)
    return templates.TemplateResponse(
        "auth_register.html",
        {"request": request, "titulo": "Criar conta • Lechare",
         "error": None,
         "disciplina": {"id": disc_id, "name": disc_name},
         "form_prev": {"name": "", "password": "", "password2": ""}}
    )

@router.post("/signup")
def post_signup(
    request: Request,
    name: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
):
    disc_id = request.cookies.get(DISC_ID_COOKIE)
    disc_name = request.cookies.get(DISC_NAME_COOKIE)
    if not disc_id:
        return RedirectResponse(url="/access", status_code=303)

    name = name.strip()
    if len(name) < 3:
        return templates.TemplateResponse(
            "auth_register.html",
            {"request": request, "titulo": "Criar conta • Lechare",
             "error": "Nome de usuário deve ter pelo menos 3 caracteres.",
             "disciplina": {"id": disc_id, "name": disc_name},
             "form_prev": {"name": name, "password": "", "password2": ""}},
            status_code=400
        )
    if password != password2:
        return templates.TemplateResponse(
            "auth_register.html",
            {"request": request, "titulo": "Criar conta • Lechare",
             "error": "As senhas não conferem.",
             "disciplina": {"id": disc_id, "name": disc_name},
             "form_prev": {"name": name, "password": "", "password2": ""}},
            status_code=400
        )

    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT COUNT(*) FROM tbl_usr WHERE no_name = :n"),
            {"n": name},
        ).scalar()
        if exists and int(exists) > 0:
            return templates.TemplateResponse(
                "auth_register.html",
                {"request": request, "titulo": "Criar conta • Lechare",
                 "error": "Esse nome de usuário já existe.",
                 "disciplina": {"id": disc_id, "name": disc_name},
                 "form_prev": {"name": name, "password": "", "password2": ""}},
                status_code=400
            )
        # grava usuário com ds_type = id_discipline
        conn.execute(
            text("INSERT INTO tbl_usr (no_name, pw_password, ds_type) VALUES (:n, :p, :t)"),
            {"n": name, "p": password, "t": str(disc_id)},
        )

    return RedirectResponse(url=f"/login?created=1&username={name}", status_code=303)
