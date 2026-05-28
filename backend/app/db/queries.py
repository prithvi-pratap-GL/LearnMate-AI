from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.database import User, Session as SessionModel, QuestionTiming
from datetime import datetime
import uuid


def create_user(db: Session, name: str):
    db_user = User(name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_or_create_user(db: Session, name: str):
    user = db.query(User).filter(User.name == name).first()
    if not user:
        user = create_user(db, name)
    return user


def create_session(db: Session, user_id: int, topic: str, round: int):
    session_uuid = str(uuid.uuid4())
    db_session = SessionModel(
        session_uuid=session_uuid,
        user_id=user_id,
        topic=topic,
        round=round,
        status="in_progress"
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_session(db: Session, session_uuid: str):
    return db.query(SessionModel).filter(SessionModel.session_uuid == session_uuid).first()


def save_question_timing(
    db: Session,
    session_id: int,
    question_index: int,
    question_text: str,
    time_spent_seconds: int,
    student_answer: str,
    correct_answer: str,
    is_correct: bool = None,
    ai_help_type: str = None
):
    ai_help_used = ai_help_type is not None

    timing = QuestionTiming(
        session_id=session_id,
        question_index=question_index,
        question_text=question_text,
        time_spent_seconds=time_spent_seconds,
        ai_help_used=ai_help_used,
        ai_help_type=ai_help_type,
        student_answer=student_answer,
        correct_answer=correct_answer,
        is_correct=is_correct
    )
    db.add(timing)
    db.commit()
    db.refresh(timing)
    return timing


def get_session_timings(db: Session, session_id: int):
    return db.query(QuestionTiming).filter(
        QuestionTiming.session_id == session_id
    ).order_by(QuestionTiming.question_index).all()


def complete_session(db: Session, session_uuid: str, status: str = "completed"):
    db_session = get_session(db, session_uuid)
    if db_session:
        db_session.status = status
        db_session.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
    return db_session


def mark_ai_help_used(db: Session, session_id: int, question_index: int, help_type: str):
    timing = db.query(QuestionTiming).filter(
        QuestionTiming.session_id == session_id,
        QuestionTiming.question_index == question_index
    ).first()

    if timing:
        timing.ai_help_used = True
        timing.ai_help_type = help_type
        db.commit()
        db.refresh(timing)
    return timing
