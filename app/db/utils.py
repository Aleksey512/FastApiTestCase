import datetime
from typing import Sequence, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Questions


async def get_questions(session: AsyncSession, skip: int = 0, limit: int = 10) -> Tuple[Sequence[Questions], int]:
    result = await session.execute(select(Questions).offset(skip).limit(limit))
    count = await session.execute(select(func.count()).select_from(Questions))
    return result.scalars().all(), count.scalar()


async def get_last_added_question(session: AsyncSession) -> Questions | None:
    result = await session.execute(select(Questions).order_by(-Questions.id))
    return result.scalars().first()


def add_question(
        session: AsyncSession,
        question: str,
        answer: str,
        source_id: int,
        created_at: datetime.datetime,
) -> Questions:
    new_question = Questions(
        question=question, source_id=source_id, answer=answer, created_at=created_at
    )
    session.add(new_question)
    return new_question
