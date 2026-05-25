from pydantic import BaseModel, Field, ConfigDict
from typing import List

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
