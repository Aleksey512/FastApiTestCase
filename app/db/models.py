import datetime
import uuid

from sqlalchemy import Column, Integer, String
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import ForeignKey

from .conn import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, default=generate_uuid, index=True)
    name = Column(String)


class Audio(Base):
    __tablename__ = "audio"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    path2file = Column(String)
    filename = Column(String)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))


class Questions(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer)
    question = Column(String, unique=True, index=True)
    answer = Column(String, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.datetime.now())
