import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Questions, Audio
from pydub import AudioSegment


async def get_users(session: AsyncSession) -> list[User]:
    """Get all Users from db"""
    result = await session.execute(select(User))
    return result.scalars().all()


async def get_user(session: AsyncSession, id: int) -> User:
    """Get User from id"""
    result = await session.execute(select(User).where(User.id == id))
    return result.scalars().first()


def add_user(session: AsyncSession, name: str) -> User:
    """Add User to db"""
    new_user = User(name=name)
    session.add(new_user)
    return new_user


async def get_questions(session: AsyncSession) -> list[Questions]:
    """Get all Questions from db"""
    result = await session.execute(select(Questions))
    return result.scalars().all()


async def get_last_added_question(sessiion: AsyncSession) -> Questions:
    result = await sessiion.execute(select(Questions).order_by(-Questions.id))
    return result.scalars().first()


def add_question(session: AsyncSession, source_id: int, question: str, answer: str,
                 created_at: datetime.datetime) -> Questions:
    """Add Questions to db"""
    new_question = Questions(question=question, source_id=source_id, answer=answer, created_at=created_at)
    session.add(new_question)
    return new_question


async def get_audio(session: AsyncSession, id: int) -> Audio:
    """Get Audio from id"""
    result = await session.execute(select(Audio).where(Audio.id == id))
    return result.scalars().first()


def add_audio(session: AsyncSession, token: str, path2file: str, user_id: int, filename: str) -> Audio:
    """Add Audio to db"""
    new_audio = Audio(token=token, user_id=user_id, path2file=path2file, filename=filename)
    session.add(new_audio)
    return new_audio


def wav2mp3(wav_file: str, filename: str, uesr_id: int, filetoken: str) -> tuple[str, str] | None:
    """Convert *.wav to *.mp3"""

    try:
        audio = AudioSegment.from_mp3(Path(wav_file))
        Path(f"./mp3/{uesr_id}/{filetoken}").mkdir(parents=True, exist_ok=True)
        filepath = f"./mp3/{uesr_id}/{filetoken}/{filename}.mp3"
        audio.export(Path(filepath), format='mp3')  # for export
        return filepath, f"{filename}.mp3"
    except Exception as e:
        print(e)
        return None
