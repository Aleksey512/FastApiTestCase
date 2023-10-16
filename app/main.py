import aiohttp
from fastapi import Depends, FastAPI, Query
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .db.conn import get_session, init_models
from .db.schemas import QuestionNumsSchema, QuestionsSchema, QuestionsSchemaWithPagination
from .db.utils import add_question, get_last_added_question, get_questions

app = FastAPI()


@app.on_event("startup")
async def db_init_models():
    """Initialize db models"""
    await init_models()
    print("Done")


@app.post("/api/questions", response_model=QuestionsSchema)
async def random_questions(
        questions_num: QuestionNumsSchema,
        session: AsyncSession = Depends(get_session),
):
    """Получает random вопрос и добавляет в БД"""

    if questions_num.questions_num <= 0 or questions_num.questions_num is None:
        return {"message": "Question num must be more than 0"}

    url = f"https://jservice.io/api/random?count={questions_num.questions_num}"

    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url) as resp:
            response = await resp.json()

    buffer = None
    count = 0

    for data in response:
        try:
            q = QuestionsSchema.model_validate(data)
        except ValidationError as e:
            raise e

        last_q = await get_last_added_question(session)
        kwargs = {
            'session': session,
            'question': q.question,
            'answer': q.answer,
            'created_at': q.created_at,
            'source_id': q.id
        }
        add_question(**kwargs)
        try:
            await session.commit()
            buffer = last_q
        except IntegrityError:
            await session.rollback()
            count += 1

    if count != 0:
        return await random_questions(QuestionNumsSchema(questions_num=count), session)

    return buffer


@app.get("/api/questions", response_model=QuestionsSchemaWithPagination)
async def get_all_questions(session: AsyncSession = Depends(get_session),
                            skip: int = Query(0, ge=0),
                            limit: int = Query(10, le=100),
                            ):
    """
    Достает все вопросы из БД с пагинацией

    :param session: AsyncSession
    :param skip: Количество элементов для пропуска (начиная с 0).
    :param limit: Максимальное количество элементов для возврата (ограничено 100).
    """
    questions, count = await get_questions(session, skip=skip, limit=limit)
    return QuestionsSchemaWithPagination(
        items=[
            QuestionsSchema(
                id=q.id,
                source_id=q.source_id,
                question=q.question,
                answer=q.answer,
                created_at=q.created_at,
            ) for q in questions],
        total_count=count)
