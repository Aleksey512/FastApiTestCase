import os
from pathlib import Path
from typing import Annotated

import aiofiles
import requests
from fastapi import Depends, Query
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .db.conn import get_session, init_models
from .db.models import generate_uuid
from .db.schemas import UserCreateSchema, QuestionsSchema, UserSchema, QuestionNumsSchema
from .db.utils import get_users, add_user, add_question, get_questions, get_user, wav2mp3, add_audio, get_audio, \
    get_last_added_question

app = FastAPI()


@app.on_event("startup")
async def db_init_models():
    """Initial db models"""
    await init_models()
    print("Done")


@app.post("/api/questions")
async def random_questions(questions_num: QuestionNumsSchema,
                           session: AsyncSession = Depends(get_session)):
    """Get a random question and add to db"""

    if questions_num.questions_num <= 0 or questions_num.questions_num is None:
        return {"message": "Question num must be more then 0"}
    url = f"https://jservice.io/api/random?count={questions_num.questions_num}"
    resp = requests.get(url)
    data = resp.json()
    buffer = None
    count = 0

    for d in data:
        q = QuestionsSchema.validate(d)
        last_q = await get_last_added_question(session)
        add_question(session, q.id, q.question, q.answer, q.created_at)
        try:
            await session.commit()
            buffer = last_q
        except IntegrityError:
            await session.rollback()
            count += 1
    if count != 0:
        return await random_questions(QuestionNumsSchema(questions_num=count), session)
    return buffer


@app.get("/api/questions")
async def get_all_questions(session: AsyncSession = Depends(get_session)):
    """Extracts all questions from db"""

    questions = await get_questions(session)
    return [QuestionsSchema(id=q.source_id, source_id=q.source_id, question=q.question, answer=q.answer,
                            created_at=q.created_at) for q in
            questions]


@app.get("/api/users")
async def get_all_users(session: AsyncSession = Depends(get_session)):
    """Extracts all users from db"""

    users = await get_users(session)
    return [UserSchema(id=u.id, token=u.token, name=u.name) for u in users]


@app.post("/api/users/add")
async def add_one_user(user: UserCreateSchema,
                       session: AsyncSession = Depends(get_session)):
    """Add User to db"""

    userAdd = add_user(session, user.name)
    try:
        await session.commit()
        return userAdd
    except Exception as e:
        print(e)
        await session.rollback()
        return JSONResponse(content={"message": "User not added"}, status_code=500)


@app.post("/api/audio/add")
async def convert_audio(file: Annotated[UploadFile, File()],
                        id: Annotated[int, Body()],
                        token: Annotated[str, Body()],
                        session: AsyncSession = Depends(get_session)):
    """Covert *.wav format to *.mp3 and save it to db"""

    if not file:
        return JSONResponse(content={"message": "No upload file sent"}, status_code=400)
    if not file.content_type.startswith("audio/"):
        return JSONResponse(content={"message": "Sent audio file"}, status_code=400)
    if not file.content_type.startswith("audio/wave") and file.filename.split('.')[-1] != "wav":
        return JSONResponse(content={"message": "Sent *.wav audio file"}, status_code=400)

    user = await get_user(session, id)
    if not user:
        return JSONResponse(content={"message": "User not found"}, status_code=404)
    if user.token != token:
        return JSONResponse(content={"message": "User token not valid"}, status_code=400)

    filetoken = generate_uuid()
    Path(f"./wav/{id}/{filetoken}").mkdir(parents=True, exist_ok=True)
    filepath = Path(f"./wav/{id}/{filetoken}/{file.filename}")
    async with aiofiles.open(filepath, 'wb') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)

    path2file, filename = wav2mp3(out_file.name, file.filename.split('.')[0], id, filetoken)
    if not path2file:
        return JSONResponse(content={"message": "File not saved"}, status_code=500)

    saved_audio = add_audio(session, filetoken, path2file, user.id, filename)
    try:
        await session.commit()
        return {
            "download": f"http://{os.getenv('PUBLIC_HOST')}:{os.getenv('PUBLIC_PORT')}/record?id={saved_audio.id}&user_id={saved_audio.user_id}"}
    except Exception as e:
        print(e)
        await session.rollback()
        return JSONResponse(content={"message": "File not saved"}, status_code=500)


@app.get("/record")
async def download_mp3(id: int | None = Query(default=None),
                       user_id: int | None = Query(default=None),
                       session: AsyncSession = Depends(get_session)):
    if not id:
        return JSONResponse(content={"message": "Not audio id sent"}, status_code=400)
    if not user_id:
        return JSONResponse(content={"message": "Not user id sent"}, status_code=400)

    audio = await get_audio(session, id)

    if not audio:
        return JSONResponse(content={"message": "Audio not found"}, status_code=404)

    if audio.user_id != user_id:
        return JSONResponse(content={"message": "Audio for a user with this id does not exist"})

    return FileResponse(path=audio.path2file, filename=audio.filename, media_type="multipart/form-data")
