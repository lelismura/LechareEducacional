from pydantic import BaseModel, ConfigDict

class DisciplinaOut(BaseModel):
    id_discipline: int
    no_discipline: str
    pw_password: str | None = None

    # permite converter direto de objetos ORM
    model_config = ConfigDict(from_attributes=True)
