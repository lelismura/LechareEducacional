from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session
from app.db import engine, get_db

# Models
from app.models.discipline import Disciplina
from app.models.questions import Question

# Schemas
from app.schemas.disciplinas import DisciplinaOut
from app.schemas.questions import QuestionOut, QuestionCreate, QuestionUpdate

router = APIRouter(tags=["public"])  # <-- ESSENCIAL

# ---------- DISCIPLINAS (ORM) ----------
@router.get("/disciplinas", response_model=list[DisciplinaOut])
def list_disciplinas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Disciplina).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()

# ---------- QUESTIONS (ORM + CRUD) ----------
@router.get("/questions", response_model=list[QuestionOut])
def list_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Question).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()

@router.get("/questions/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    obj = db.get(Question, question_id)
    if not obj:
        raise HTTPException(404, "Pergunta não encontrada")
    return obj

@router.post("/questions", response_model=QuestionOut, status_code=201)
def create_question(data: QuestionCreate, db: Session = Depends(get_db)):
    obj = Question(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.patch("/questions/{question_id}", response_model=QuestionOut)
def update_question(question_id: int, data: QuestionUpdate, db: Session = Depends(get_db)):
    obj = db.get(Question, question_id)
    if not obj:
        raise HTTPException(404, "Pergunta não encontrada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
