from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_uuid = Column(String(36), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    round = Column(Integer, nullable=False)
    status = Column(String(50), default="in_progress", nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
    question_timings = relationship("QuestionTiming", back_populates="session")


class AIHelpType(str, enum.Enum):
    HINT = "hint"
    EXPLANATION = "explanation"


class QuestionTiming(Base):
    __tablename__ = "question_timings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    question_index = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    time_spent_seconds = Column(Integer, nullable=False)
    ai_help_used = Column(Boolean, default=False)
    ai_help_type = Column(String(50), nullable=True)
    student_answer = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="question_timings")
