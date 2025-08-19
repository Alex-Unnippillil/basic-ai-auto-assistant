"""Database models and helpers for quiz automation persistence."""

from __future__ import annotations

from sqlalchemy import Column, Float, Integer, create_engine
from sqlalchemy.orm import declarative_base

from .config import settings

Base = declarative_base()


class Question(Base):
    """Model storing per-question metrics."""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    duration = Column(Float, nullable=False)
    tokens = Column(Integer, nullable=False)


class SessionStat(Base):
    """Aggregated statistics for a quiz session."""

    __tablename__ = "session_stats"

    id = Column(Integer, primary_key=True)
    total_time = Column(Float, default=0.0)
    total_tokens = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    errors = Column(Integer, default=0)


def get_engine(url: str | None = None):
    """Return a SQLAlchemy engine for *url* or the configured database."""
    return create_engine(url or settings.database_url or "sqlite:///quiz.db")


def migrate(url: str | None = None) -> None:
    """Create database tables if they do not already exist."""
    engine = get_engine(url)
    Base.metadata.create_all(engine)
