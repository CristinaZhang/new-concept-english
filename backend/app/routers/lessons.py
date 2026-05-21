from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_session
from app.db.models import Lesson

router = APIRouter(tags=["lessons"])


@router.get("/lessons")
def list_lessons(
    level: Optional[str] = "第一册",
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session),
) -> dict:
    stmt = select(Lesson)
    if level:
        stmt = stmt.where(Lesson.level == level)
    stmt = stmt.order_by(Lesson.lesson_number).offset(offset).limit(limit)
    items = session.exec(stmt).all()

    count_stmt = select(Lesson)
    if level:
        count_stmt = count_stmt.where(Lesson.level == level)
    total = len(session.exec(count_stmt).all())

    return {
        "items": [
            {
                "id": l.id,
                "lesson_number": l.lesson_number,
                "title": l.title,
                "level": l.level,
                "audio_url": l.audio_url,
            }
            for l in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/lessons/{lesson_id}")
def get_lesson(
    lesson_id: int,
    session: Session = Depends(get_session),
) -> dict:
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {
        "id": lesson.id,
        "lesson_number": lesson.lesson_number,
        "title": lesson.title,
        "level": lesson.level,
        "text": lesson.text,
        "translation": lesson.translation,
        "image_url": lesson.image_url,
        "audio_url": lesson.audio_url,
    }


@router.get("/lessons/{lesson_id}/vocabulary")
def get_lesson_vocabulary(
    lesson_id: int,
    session: Session = Depends(get_session),
) -> list[dict]:
    from app.db.models import Vocabulary

    stmt = select(Vocabulary).where(Vocabulary.lesson_id == lesson_id)
    items = session.exec(stmt).all()
    return [
        {
            "id": v.id,
            "lesson_id": v.lesson_id,
            "word": v.word,
            "phonetic": v.phonetic,
            "meaning": v.meaning,
            "example_sentence": v.example_sentence,
            "audio_url": v.audio_url,
        }
        for v in items
    ]


@router.get("/lessons/{lesson_id}/grammar")
def get_lesson_grammar(
    lesson_id: int,
    session: Session = Depends(get_session),
) -> list[dict]:
    from app.db.models import GrammarPoint

    stmt = select(GrammarPoint).where(GrammarPoint.lesson_id == lesson_id)
    items = session.exec(stmt).all()
    return [
        {
            "id": g.id,
            "lesson_id": g.lesson_id,
            "name": g.name,
            "explanation": g.explanation,
            "examples": g.examples,
        }
        for g in items
    ]
