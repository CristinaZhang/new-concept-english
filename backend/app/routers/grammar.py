from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db.database import get_session
from app.db.models import GrammarPoint, Exercise

router = APIRouter(tags=["grammar"])


class ExerciseSubmitRequest(BaseModel):
    answer: str


class ExerciseSubmitResponse(BaseModel):
    correct: bool
    correct_answer: str
    user_answer: str


@router.get("/grammar/{grammar_id}")
def get_grammar(
    grammar_id: int,
    session: Session = Depends(get_session),
) -> dict:
    g = session.get(GrammarPoint, grammar_id)
    if not g:
        raise HTTPException(status_code=404, detail="Grammar point not found")
    return {
        "id": g.id,
        "lesson_id": g.lesson_id,
        "name": g.name,
        "explanation": g.explanation,
        "examples": g.examples,
    }


@router.get("/exercises/{lesson_id}")
def get_exercises(
    lesson_id: int,
    session: Session = Depends(get_session),
) -> list[dict]:
    stmt = select(Exercise).where(Exercise.lesson_id == lesson_id)
    items = session.exec(stmt).all()
    return [
        {
            "id": e.id,
            "lesson_id": e.lesson_id,
            "grammar_point_id": e.grammar_point_id,
            "type": e.type,
            "question": e.question,
            "options": e.options,
            # answer is intentionally NOT returned (front-end submits it)
        }
        for e in items
    ]


@router.post("/exercises/{exercise_id}/submit", response_model=ExerciseSubmitResponse)
def submit_exercise(
    exercise_id: int,
    req: ExerciseSubmitRequest,
    session: Session = Depends(get_session),
) -> ExerciseSubmitResponse:
    e = session.get(Exercise, exercise_id)
    if not e:
        raise HTTPException(status_code=404, detail="Exercise not found")
    # case-insensitive comparison for text answers
    correct = req.answer.strip().lower() == e.answer.strip().lower()
    return ExerciseSubmitResponse(
        correct=correct,
        correct_answer=e.answer,
        user_answer=req.answer,
    )
