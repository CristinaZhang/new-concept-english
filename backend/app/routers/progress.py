from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db.database import get_session
from app.db.models import Lesson, UserProgress

router = APIRouter(tags=["progress"])


class UpdateProgressRequest(BaseModel):
    vocabulary_score: int = 0
    grammar_score: int = 0


@router.get("/progress")
def get_all_progress(
    session: Session = Depends(get_session),
) -> list[dict]:
    stmt = select(UserProgress).order_by(UserProgress.completed_at.desc())
    items = session.exec(stmt).all()
    return [
        {
            "id": p.id,
            "lesson_id": p.lesson_id,
            "vocabulary_score": p.vocabulary_score,
            "grammar_score": p.grammar_score,
            "completed_at": p.completed_at,
            "review_dates": p.review_dates,
        }
        for p in items
    ]


@router.post("/progress/lessons/{lesson_id}")
def update_progress(
    lesson_id: int,
    req: UpdateProgressRequest,
    session: Session = Depends(get_session),
) -> dict:
    # Verify lesson exists
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Upsert progress
    stmt = select(UserProgress).where(UserProgress.lesson_id == lesson_id)
    progress = session.exec(stmt).first()

    if progress:
        progress.vocabulary_score = req.vocabulary_score
        progress.grammar_score = req.grammar_score
        progress.completed_at = datetime.now(timezone.utc)
    else:
        progress = UserProgress(
            lesson_id=lesson_id,
            vocabulary_score=req.vocabulary_score,
            grammar_score=req.grammar_score,
            completed_at=datetime.now(timezone.utc),
        )
        session.add(progress)

    session.commit()
    session.refresh(progress)

    return {
        "id": progress.id,
        "lesson_id": progress.lesson_id,
        "vocabulary_score": progress.vocabulary_score,
        "grammar_score": progress.grammar_score,
        "completed_at": progress.completed_at,
        "review_dates": progress.review_dates,
    }


@router.get("/progress/summary")
def get_progress_summary(
    session: Session = Depends(get_session),
) -> dict:
    # Total lessons
    total_lessons = len(session.exec(select(Lesson)).all())
    # Completed lessons
    completed = len(session.exec(select(UserProgress)).all())
    # Average scores
    all_progress = session.exec(select(UserProgress)).all()
    if all_progress:
        avg_vocab = round(sum(p.vocabulary_score for p in all_progress) / len(all_progress), 1)
        avg_grammar = round(sum(p.grammar_score for p in all_progress) / len(all_progress), 1)
    else:
        avg_vocab = 0.0
        avg_grammar = 0.0

    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed,
        "completion_rate": round(completed / total_lessons * 100, 1) if total_lessons else 0,
        "average_vocabulary_score": avg_vocab,
        "average_grammar_score": avg_grammar,
    }
