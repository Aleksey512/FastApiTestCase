import datetime
from typing import Optional

from pydantic import BaseModel


class QuestionNumsSchema(BaseModel):
    questions_num: int | None


class QuestionsSchema(BaseModel):
    id: int
    source_id: Optional[int] = None
    question: str
    answer: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class QuestionsSchemaWithPagination(BaseModel):
    items: list[QuestionsSchema]
    total_count: int
