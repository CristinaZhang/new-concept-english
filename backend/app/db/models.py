from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Lesson(SQLModel, table=True):
    __tablename__ = "lesson"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_number: int = Field(index=True, unique=True)
    title: str
    level: str = "第一册"
    text: str = ""
    translation: str = ""
    image_url: Optional[str] = None
    audio_url: Optional[str] = None

    vocabularies: list["Vocabulary"] = Relationship(back_populates="lesson")
    grammar_points: list["GrammarPoint"] = Relationship(back_populates="lesson")
    exercises: list["Exercise"] = Relationship(back_populates="lesson")
    progress: Optional["UserProgress"] = Relationship(back_populates="lesson")


class Vocabulary(SQLModel, table=True):
    __tablename__ = "vocabulary"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id", index=True)
    word: str
    phonetic: str = ""
    meaning: str
    example_sentence: str = ""
    audio_url: Optional[str] = None

    lesson: Optional["Lesson"] = Relationship(back_populates="vocabularies")


class GrammarPoint(SQLModel, table=True):
    __tablename__ = "grammar_point"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id", index=True)
    name: str
    explanation: str
    examples_json: str = "[]"

    lesson: Optional["Lesson"] = Relationship(back_populates="grammar_points")
    exercises: list["Exercise"] = Relationship(back_populates="grammar_point")

    @property
    def examples(self) -> list:
        import json
        return json.loads(self.examples_json or "[]")

    @examples.setter
    def examples(self, value: list) -> None:
        import json
        self.examples_json = json.dumps(value, ensure_ascii=False)


class Exercise(SQLModel, table=True):
    __tablename__ = "exercise"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id", index=True)
    grammar_point_id: Optional[int] = Field(default=None, foreign_key="grammar_point.id")
    type: str
    question: str
    answer: str
    options_json: str = "[]"

    lesson: Optional["Lesson"] = Relationship(back_populates="exercises")
    grammar_point: Optional["GrammarPoint"] = Relationship(back_populates="exercises")

    @property
    def options(self) -> list:
        import json
        return json.loads(self.options_json or "[]")

    @options.setter
    def options(self, value: list) -> None:
        import json
        self.options_json = json.dumps(value, ensure_ascii=False)


class UserProgress(SQLModel, table=True):
    __tablename__ = "user_progress"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id", unique=True, index=True)
    vocabulary_score: int = 0
    grammar_score: int = 0
    completed_at: Optional[datetime] = None
    review_dates_json: str = "[]"

    lesson: Optional["Lesson"] = Relationship(back_populates="progress")

    @property
    def review_dates(self) -> list:
        import json
        return json.loads(self.review_dates_json or "[]")

    @review_dates.setter
    def review_dates(self, value: list) -> None:
        import json
        self.review_dates_json = json.dumps(value, ensure_ascii=False)
