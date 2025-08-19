from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Question(Base):
    __tablename__ = "tbl_questions"
    id_question: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ds_question: Mapped[str] = mapped_column(Text, nullable=False)
    ds_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    ds_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
