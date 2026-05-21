from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


# ── Lesson ────────────────────────────────────────────────────────────

class Lesson(SQLModel, table=True):
    __tablename__ = "lesson"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_number: int = Field(index=True, unique=True)  # 1-144
    title: str
    level: str = "第一册"
    text: str = ""  # 课文原文
    translation: str = ""  # 中文翻译
    image_url: Optional[str] = None
    audio_url: Optional[str] = None

    # relationships
    vocabularies: list["Vocabulary"] = Relationship(back_populates="lesson")
    grammar_points: list["GrammarPoint"] = Relationship(back_populates="lesson")
    exercises: list["Exercise"] = Relationship(back_populates="lesson")
    progress: Optional["UserProgress"] = Relationship(back_populates="lesson")


# ── Vocabulary ────────────────────────────────────────────────────────

class Vocabulary(SQLModel, table=True):
    __tablename__ = "vocabulary"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id", index=True)
    word: str
    phonetic: str = ""
    meaning: str  # 中文释义
    example_sentence: str = ""
    audio_url: Optional[str] = None

    lesson: Optional["Lesson"] = Relationship(back_populates="vocabularies")


# ── GrammarPoint ──────────────────────────────────────────────────────

class GrammarPoint(SQLModel, table=True):
    __tablename__ = "grammar_point"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id", index=True)
    name: str  # 语法点名称
    explanation: str  # 中文解释
    examples_json: str = "[]"  # JSON array of example sentences

    lesson: Optional["Lesson"] = Relationship(back_populates="grammar_points")
    exercises: list["Exercise"] = Relationship(back_populates="grammar_point")

    @property
    def examples(self) -> list[str]:
        return json.loads(self.examples_json or "[]")

    @examples.setter
    def examples(self, value: list[str]) -> None:
        self.examples_json = json.dumps(value, ensure_ascii=False)


# ── Exercise ──────────────────────────────────────────────────────────

class Exercise(SQLModel, table=True):
    __tablename__ = "exercise"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id", index=True)
    grammar_point_id: Optional[int] = Field(default=None, foreign_key="grammar_point.id")
    type: str  # fill_blank | mc | error_correction
    question: str
    answer: str
    options_json: str = "[]"  # JSON array for multiple choice

    lesson: Optional["Lesson"] = Relationship(back_populates="exercises")
    grammar_point: Optional["GrammarPoint"] = Relationship(back_populates="exercises")

    @property
    def options(self) -> list[str]:
        return json.loads(self.options_json or "[]")

    @options.setter
    def options(self, value: list[str]) -> None:
        self.options_json = json.dumps(value, ensure_ascii=False)


# ── UserProgress (single-user, no auth needed) ───────────────────────

class UserProgress(SQLModel, table=True):
    __tablename__ = "user_progress"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id", unique=True, index=True)
    vocabulary_score: int = 0  # 0-100
    grammar_score: int = 0  # 0-100
    completed_at: Optional[datetime] = None
    review_dates_json: str = "[]"  # JSON array of ISO date strings

    lesson: Optional["Lesson"] = Relationship(back_populates="progress")

    @property
    def review_dates(self) -> list[str]:
        return json.loads(self.review_dates_json or "[]")

    @review_dates.setter
    def review_dates(self, value: list[str]) -> None:
        self.review_dates_json = json.dumps(value, ensure_ascii=False)
