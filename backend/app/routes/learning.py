from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from app.models.schemas import LearningAnalysisRequest
from app.services import (
    evaluation_service,
    challenge_service,
    roadmap_service,
    question_service,
)
import json
import logging
import re

router = APIRouter()
ROUND_1_QUESTION_COUNT = 5

# It's best to configure logging in main.py, but for demonstration:
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


def sanitize_input(text: str, max_length: int = 100) -> str:
    """
    Sanitizes user input to prevent prompt injection.
    - Limits length to prevent overly long inputs.
    - Removes characters other than letters, numbers, and spaces.
    """
    if not text:
        return ""
    # Limit length first
    sanitized = text[:max_length]
    # Remove potentially malicious characters
    sanitized = re.sub(r"[^a-zA-Z0-9\s]", "", sanitized)
    return sanitized.strip()


class TopicRequest(BaseModel):
    topic: str
    difficulty: str = "beginner"


class Round1SubmissionRequest(BaseModel):
    student_name: str
    topic: str
    questions: list


class Round2SubmissionRequest(BaseModel):
    student_name: str
    topic: str
    questions: list
    round_1_score: int
    round_1_evaluation: dict


@router.post("/generate-questions")
async def generate_questions(http_request: Request):
    """Generate exactly 5 questions for Round 1"""
    try:
        body_bytes = await http_request.body()
        body_str = body_bytes.decode("utf-8")
        body = json.loads(body_str)
        topic = sanitize_input(body.get("topic", "General"))

        result = await question_service.generate_questions(
            topic,
            difficulty="beginner"
        )

        questions = result["questions"][
            :ROUND_1_QUESTION_COUNT
        ]

        return {
            "questions": questions,
            "round": 1,
            "total_questions": len(
                questions
            ),
            "source": result.get(
                "source",
                "llm",
            ),
        }
    
    except Exception as e:
        log.error(f"Failed to generate questions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating questions.",
        )


@router.post("/submit-round-1")
async def submit_round_1(request: Round1SubmissionRequest):
    """
    Submit Round 1 answers and evaluate.
    Returns score and determines if user moves to Round 2 or gets results.
    """
    try:
        from app.models.schemas import QuestionAnswer

        questions_list = [
            QuestionAnswer(**q) if isinstance(q, dict) else q for q in request.questions
        ]
        analysis_request = LearningAnalysisRequest(
            student_name=request.student_name,
            topic=sanitize_input(request.topic),
            questions=questions_list,
        )

        # Evaluate Round 1
        evaluation = await evaluation_service.evaluate_learning(analysis_request)
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        weak_areas = evaluation.get("weak_areas", [])
        level = evaluation.get("level", "Beginner")

        # Generate roadmap (one level higher than current)
        sanitized_topic = sanitize_input(request.topic)
        roadmap_content = await roadmap_service.generate_roadmap(
            level, strengths, weak_areas, score, sanitized_topic
        )
        roadmap = {
            "title": f"Personalized Roadmap for {level}",
            "content": roadmap_content,
        }

        if score < 50:
            # User scores below 50% - show results page with performance analysis
            questions_dict = [
                q.model_dump() if hasattr(q, "model_dump") else q
                for q in questions_list
            ]
            content = await challenge_service.generate_performance_analysis(
                sanitized_topic, questions_dict, score
            )
            generated_content = {"type": "performance_analysis", "content": content}

            return {
                "status": "completed",
                "round": 1,
                "evaluation": evaluation,
                "generated_content": generated_content,
                "roadmap": roadmap,
                "can_proceed_to_round_2": False,
            }
        else:
            # User scores 50% or above - proceed to Round 2
            return {
                "status": "proceed_to_round_2",
                "round": 1,
                "score": score,
                "evaluation": evaluation,
                "can_proceed_to_round_2": True,
            }
    except Exception as e:
        log.error(f"Error in /submit-round-1: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An internal error occurred during evaluation."
        )


def _extract_keywords(question: str) -> set:
    """Extract key technical terms from a question for similarity detection."""
    ignore_words = {
        "what",
        "is",
        "a",
        "the",
        "an",
        "in",
        "of",
        "to",
        "for",
        "or",
        "and",
        "by",
        "with",
        "on",
        "at",
        "this",
        "that",
        "are",
        "does",
        "do",
        "can",
        "which",
        "how",
        "you",
        "your",
        "used",
    }
    words = set(question.lower().split())
    return {w for w in words if len(w) > 3 and w not in ignore_words}


def _are_questions_similar(q1: str, q2: str) -> bool:
    """Check if two questions are semantically similar by comparing keywords."""
    keywords1 = _extract_keywords(q1)
    keywords2 = _extract_keywords(q2)

    if not keywords1 or not keywords2:
        return False

    overlap = len(keywords1 & keywords2)
    similarity = overlap / min(len(keywords1), len(keywords2))
    return similarity > 0.5


@router.post("/generate-round-2-questions")
async def generate_round_2_questions(http_request: Request):
    """Generate advanced challenge questions for Round 2, excluding Round 1 questions"""
    try:
        body_bytes = await http_request.body()
        body_str = body_bytes.decode("utf-8")
        body = json.loads(body_str)
        topic = sanitize_input(body.get("topic", "General"))
        round_1_questions = body.get("round_1_questions", [])

        # Generate more advanced questions
        result = await question_service.generate_questions(
            topic,
            difficulty="advanced"
        )

        questions = result["questions"]

        # Filter out questions that were in Round 1 (exact match and similar)
        round_1_q_texts = [q.get("question", "").lower() for q in round_1_questions]
        filtered_questions = [
            q
            for q in questions
            if q.get("question", "").lower() not in round_1_q_texts
            and not any(
                _are_questions_similar(q.get("question", ""), r1q)
                for r1q in round_1_q_texts
            )
        ]

        # Ensure we have 5 unique questions (retry if filtered too many)
        attempts = 0
        all_questions = filtered_questions[:]
        while len(all_questions) < 5 and attempts < 4:

            more_result = await question_service.generate_questions(...)

            more_questions = more_result["questions"]
            
            for q in more_questions:
                if (
                    q.get("question", "").lower() not in round_1_q_texts
                    and not any(
                        _are_questions_similar(q.get("question", ""), r1q)
                        for r1q in round_1_q_texts
                    )
                    and q not in all_questions
                    and not any(
                        _are_questions_similar(
                            q.get("question", ""), aq.get("question", "")
                        )
                        for aq in all_questions
                    )
                ):
                    all_questions.append(q)
                    if len(all_questions) >= 5:
                        break
            attempts += 1

        final_questions = all_questions[:5]
        if len(final_questions) < 5:
            log.warning(
                f"Could not generate 5 unique advanced questions for topic '{topic}'. Got {len(final_questions)}."
            )

        return {
            "questions": final_questions,
            "round": 2,
            "total_questions": len(final_questions),
        }
    except Exception as e:
        log.error(f"Error in /generate-round-2-questions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to generate Round 2 questions."
        )


@router.post("/submit-round-2")
async def submit_round_2(request: Round2SubmissionRequest):
    """
    Submit Round 2 answers and provide detailed analysis with roadmap.
    """
    try:
        from app.models.schemas import QuestionAnswer

        questions_list = [
            QuestionAnswer(**q) if isinstance(q, dict) else q for q in request.questions
        ]
        analysis_request = LearningAnalysisRequest(
            student_name=request.student_name,
            topic=sanitize_input(request.topic),
            questions=questions_list,
        )

        # Evaluate Round 2
        evaluation = await evaluation_service.evaluate_learning(analysis_request)
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        weak_areas = evaluation.get("weak_areas", [])
        level = evaluation.get("level", "Advanced")

        # Generate solution explanations
        sanitized_topic = sanitize_input(request.topic)
        questions_dict = [
            q.model_dump() if hasattr(q, "model_dump") else q for q in questions_list
        ]
        content = await challenge_service.generate_solution_explanation(
            sanitized_topic, questions_dict, score
        )
        generated_content = {"type": "solution", "content": content}

        # Generate roadmap (one level higher than current)
        roadmap_content = await roadmap_service.generate_roadmap(
            level, strengths, weak_areas, score, sanitized_topic
        )
        roadmap = {
            "title": f"Personalized Roadmap for {level}",
            "content": roadmap_content,
        }

        return {
            "status": "completed",
            "round": 2,
            "round_1_score": request.round_1_score,
            "round_2_evaluation": evaluation,
            "generated_content": generated_content,
            "roadmap": roadmap,
            "questions": questions_dict,
        }
    except Exception as e:
        log.error(f"Round 2 submission failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred during the final analysis.",
        )


@router.post("/analyze-learning")
async def analyze_learning(request: LearningAnalysisRequest):
    """Legacy endpoint for backwards compatibility"""
    try:
        evaluation = await evaluation_service.evaluate_learning(request)
        sanitized_topic = sanitize_input(request.topic)
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        weak_areas = evaluation.get("weak_areas", [])
        level = evaluation.get("level", "Beginner")

        generated_content = {}
        questions_list = request.questions
        if score < 50:
            questions_dict = [
                q.model_dump() if hasattr(q, "model_dump") else q
                for q in questions_list
            ]
            content = await challenge_service.generate_performance_analysis(
                sanitized_topic, questions_dict, score
            )
            generated_content = {"type": "performance_analysis", "content": content}
        else:
            content = await challenge_service.generate_advanced_challenges(
                sanitized_topic, strengths, score, level
            )
            generated_content = {"type": "advanced_challenges", "content": content}

        roadmap_content = await roadmap_service.generate_roadmap(
            level, strengths, weak_areas, score, sanitized_topic
        )
        roadmap = {
            "title": f"Personalized Roadmap for {level}",
            "content": roadmap_content,
        }

        return {
            "evaluation": evaluation,
            "generated_content": generated_content,
            "roadmap": roadmap,
        }
    except Exception as e:
        log.error(f"Error in /analyze-learning: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An internal error occurred during analysis."
        )
