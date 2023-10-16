import datetime

from sqlalchemy import Column, Integer, String
from sqlalchemy.types import TIMESTAMP

from .conn import Base


class Questions(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, index=True)
    question = Column(String, unique=True)
    answer = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.datetime.now())
