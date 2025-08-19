from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Disciplina(Base):
    __tablename__ = "tbl_discipline"
    id_discipline: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    no_discipline: Mapped[str] = mapped_column(String(255), nullable=False)
    pw_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
