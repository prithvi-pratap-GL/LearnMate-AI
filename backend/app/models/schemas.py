from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime

class QuestionAnswer(BaseModel):
    question: str
    correct_answer: str
    student_answer: str
    options: List[str] = []

    model_config = ConfigDict(str_strip_whitespace=True)

class LearningAnalysisRequest(BaseModel):
    student_name: str
    topic: str
    questions: List[QuestionAnswer]

    model_config = ConfigDict(str_strip_whitespace=True)


# New schemas for session and timing features
class CreateSessionRequest(BaseModel):
    student_name: str
    topic: str
    round: int

    model_config = ConfigDict(str_strip_whitespace=True)


class SessionResponse(BaseModel):
    session_uuid: str
    created_at: datetime
    topic: str
    round: int

    model_config = ConfigDict(from_attributes=True)


class AskAIRequest(BaseModel):
    session_uuid: str
    question_index: int
    question_text: str
    help_type: Literal["hint", "explanation"]

    model_config = ConfigDict(str_strip_whitespace=True)


class AskAIResponse(BaseModel):
    content: str
    help_type: str


class SaveQuestionTimingRequest(BaseModel):
    session_uuid: str
    question_index: int
    question_text: str
    time_spent_seconds: int
    student_answer: str
    correct_answer: str
    is_correct: Optional[bool] = None
    ai_help_type: Optional[str] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class CompleteSessionRequest(BaseModel):
    session_uuid: str
    status: Literal["completed", "abandoned"] = "completed"

    model_config = ConfigDict(str_strip_whitespace=True)
