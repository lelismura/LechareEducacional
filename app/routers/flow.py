from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import text
from app.db import engine
from app.web import templates

router = APIRouter()

# caches leves para não consultar toda hora
_PASS_COL = None
_QCOLS = None  # {"id": "...", "q": "...", "a": "...", "c": "..."}


def _get_pass_column(conn) -> str:
    """Descobre se a senha da disciplina está em pw_password ou ds_password."""
    global _PASS_COL
    if _PASS_COL:
        return _PASS_COL

    if conn.execute(text("SHOW COLUMNS FROM tbl_discipline LIKE 'pw_password'")).fetchone():
        _PASS_COL = "pw_password"
        return _PASS_COL

    if conn.execute(text("SHOW COLUMNS FROM tbl_discipline LIKE 'ds_password'")).fetchone():
        _PASS_COL = "ds_password"
        return _PASS_COL

    # padrão — se não existir, o erro ficará claro na consulta seguinte
    _PASS_COL = "pw_password"
    return _PASS_COL


def _get_question_columns(conn):
    """
    Detecta nomes das colunas em tbl_questions para:
      - id  (id da pergunta)
      - q   (texto da pergunta)
      - a   (resposta)
      - c   (comentário/explicação)
    Retorna dict com chaves "id","q","a","c".
    """
    global _QCOLS
    if _QCOLS:
        return _QCOLS

    rows = conn.execute(text("SHOW COLUMNS FROM tbl_questions")).mappings().all()
    names = {r["Field"] for r in rows}
    lower = {n.lower(): n for n in names}

    def pick(candidates, substr=None, default=None):
        # 1) nomes exatos em ordem de preferência
        for cand in candidates:
            if cand in names:
                return cand
            if cand.lower() in lower:
                return lower[cand.lower()]
        # 2) heurística por substring
        if substr:
            for n in names:
                if any(s in n.lower() for s in substr):
                    return n
        return default

    id_col = pick(
        ["id_question", "id_questao", "id"],
        substr=["id_question", "questao", "question"],
        default="id_question",
    )
    q_col = pick(
        ["tx_question", "ds_question", "no_question", "tx_pergunta", "pergunta"],
        substr=["question", "pergunta", "enunciado"],
        default="tx_question",
    )
    a_col = pick(
        ["tx_answer", "ds_answer", "resposta"],
        substr=["answer", "resposta"],
        default="tx_answer",
    )
    c_col = pick(
        ["tx_comment", "ds_comment", "comentario", "tx_explanation", "explanation"],
        substr=["comment", "coment", "explic", "explan"],
        default="tx_comment",
    )

    _QCOLS = {"id": id_col, "q": q_col, "a": a_col, "c": c_col}
    return _QCOLS


@router.get("/", response_class=HTMLResponse)
def root() -> RedirectResponse:
    return RedirectResponse(url="/start", status_code=307)


@router.get("/start", response_class=HTMLResponse)
def start_get(request: Request):
    err = request.query_params.get("err", "")
    err_msg = None
    if err == "1":
        err_msg = "Senha inválida. Solicite ao professor a senha correta."
    elif err == "db":
        err_msg = "Erro ao conectar ao banco de dados."

    with engine.connect() as conn:
        discs = conn.execute(
            text("SELECT id_discipline, no_discipline FROM tbl_discipline ORDER BY id_discipline")
        ).mappings().all()

    return templates.TemplateResponse(
        "flow_start.html",
        {"request": request, "titulo": "Lechare Educacional", "err": err_msg, "disciplinas": discs},
    )


@router.post("/start")
def start_post(request: Request, disc_id: int = Form(...), password: str = Form(...)):
    try:
        with engine.connect() as conn:
            pass_col = _get_pass_column(conn)
            row = conn.execute(
                text(
                    f"SELECT no_discipline, {pass_col} AS pw "
                    "FROM tbl_discipline WHERE id_discipline = :id"
                ),
                {"id": disc_id},
            ).mappings().first()
    except Exception:
        return RedirectResponse(url="/start?err=db", status_code=303)

    if not row or (row["pw"] or "") != (password or ""):
        return RedirectResponse(url="/start?err=1", status_code=303)

    resp = RedirectResponse(url="/quiz", status_code=303)
    resp.set_cookie("educapp_disc_id", str(disc_id), max_age=60 * 60 * 24 * 30, httponly=False)
    resp.set_cookie("educapp_disc_name", row["no_discipline"], max_age=60 * 60 * 24 * 30, httponly=False)
    return resp


@router.get("/quiz", response_class=HTMLResponse)
def quiz(request: Request):
    disc_id = request.cookies.get("educapp_disc_id")
    disc_name = request.cookies.get("educapp_disc_name")
    if not disc_id:
        return RedirectResponse(url="/start", status_code=303)

    with engine.connect() as conn:
        cols = _get_question_columns(conn)
        # monta SELECT com alias padronizado (tx_question, tx_answer, tx_comment)
        sql = text(
            f"""
            SELECT {cols['id']}   AS id_question,
                   {cols['q']}    AS tx_question,
                   {cols['a']}    AS tx_answer,
                   {cols['c']}    AS tx_comment
            FROM tbl_questions
            WHERE id_discipline = :d
            ORDER BY RAND()
            LIMIT 1
            """
        )
        q = conn.execute(sql, {"d": int(disc_id)}).mappings().first()

    return templates.TemplateResponse(
        "flow_quiz.html",
        {"request": request, "titulo": "Quiz", "disc": {"id": disc_id, "name": disc_name}, "q": q},
    )


@router.get("/bye", response_class=HTMLResponse)
def bye(request: Request):
    resp = templates.TemplateResponse("flow_bye.html", {"request": request, "titulo": "Até logo!"})
    resp.delete_cookie("educapp_disc_id")
    resp.delete_cookie("educapp_disc_name")
    return resp
