from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db.database import get_session
from app.db.models import Lesson, PersonalVocabulary

router = APIRouter(tags=["personal-vocabulary"])


class AddPersonalVocabRequest(BaseModel):
    lesson_id: int
    word: str
    phonetic: str = ""
    meaning: str = ""


class PersonalVocabResponse(BaseModel):
    id: int
    user_id: str
    lesson_id: int
    word: str
    phonetic: str
    meaning: str


@router.get("/v1/personal-vocab", response_model=list[PersonalVocabResponse])
def list_personal_vocab(
    user_id: str = Query(default="default"),
    lesson_id: int | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[PersonalVocabResponse]:
    """List personal vocabulary for a user, optionally filtered by lesson."""
    stmt = select(PersonalVocabulary).where(PersonalVocabulary.user_id == user_id)
    if lesson_id:
        stmt = stmt.where(PersonalVocabulary.lesson_id == lesson_id)
    stmt = stmt.order_by(PersonalVocabulary.created_at.desc())
    items = session.exec(stmt).all()
    return [
        PersonalVocabResponse(
            id=p.id,
            user_id=p.user_id,
            lesson_id=p.lesson_id,
            word=p.word,
            phonetic=p.phonetic,
            meaning=p.meaning,
        )
        for p in items
    ]


@router.post("/v1/personal-vocab", response_model=PersonalVocabResponse)
def add_personal_vocab(
    req: AddPersonalVocabRequest,
    user_id: str = Query(default="default"),
    session: Session = Depends(get_session),
) -> PersonalVocabResponse:
    """Add a word to personal vocabulary."""
    # Verify lesson exists
    lesson = session.get(Lesson, req.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Check duplicate
    existing = session.exec(
        select(PersonalVocabulary).where(
            PersonalVocabulary.user_id == user_id,
            PersonalVocabulary.lesson_id == req.lesson_id,
            PersonalVocabulary.word == req.word,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Word '{req.word}' already in personal vocab")

    pv = PersonalVocabulary(
        user_id=user_id,
        lesson_id=req.lesson_id,
        word=req.word,
        phonetic=req.phonetic,
        meaning=req.meaning,
        created_at=datetime.now(timezone.utc),
    )
    session.add(pv)
    session.commit()
    session.refresh(pv)

    return PersonalVocabResponse(
        id=pv.id,
        user_id=pv.user_id,
        lesson_id=pv.lesson_id,
        word=pv.word,
        phonetic=pv.phonetic,
        meaning=pv.meaning,
    )


@router.delete("/v1/personal-vocab/{vocab_id}")
def delete_personal_vocab(
    vocab_id: int,
    user_id: str = Query(default="default"),
    session: Session = Depends(get_session),
) -> dict:
    """Delete a personal vocabulary entry."""
    pv = session.exec(
        select(PersonalVocabulary).where(
            PersonalVocabulary.id == vocab_id,
            PersonalVocabulary.user_id == user_id,
        )
    ).first()
    if not pv:
        raise HTTPException(status_code=404, detail="Personal vocab not found")

    session.delete(pv)
    session.commit()
    return {"deleted": vocab_id}
