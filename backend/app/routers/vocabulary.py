from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_session
from app.db.models import Vocabulary

router = APIRouter(tags=["vocabulary"])


@router.get("/vocabulary/{vocab_id}")
def get_vocabulary(
    vocab_id: int,
    session: Session = Depends(get_session),
) -> dict:
    v = session.get(Vocabulary, vocab_id)
    if not v:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    return {
        "id": v.id,
        "lesson_id": v.lesson_id,
        "word": v.word,
        "phonetic": v.phonetic,
        "meaning": v.meaning,
        "example_sentence": v.example_sentence,
        "audio_url": v.audio_url,
    }
