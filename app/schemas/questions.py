from pydantic import BaseModel, Field, ConfigDict

class QuestionBase(BaseModel):
    ds_question: str = Field(..., min_length=3)
    ds_answer: str | None = None
    ds_comment: str | None = None

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    ds_question: str | None = Field(None, min_length=3)
    ds_answer: str | None = None
    ds_comment: str | None = None

class QuestionOut(QuestionBase):
    id_question: int
    model_config = ConfigDict(from_attributes=True)
