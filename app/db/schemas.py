import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserCreateSchema(BaseModel):
    name: str


class UserSchema(BaseModel):
    name: Optional[str]
    id: int
    token: str

    class Config:
        orm_mode = True


class QuestionsSchema(BaseModel):
    id: int
    source_id: Optional[int]
    question: str
    answer: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True
