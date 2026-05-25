from fastapi import APIRouter, Request
from fastapi.responses import Response
from pydantic import BaseModel
from app.models.schemas import LearningAnalysisRequest
from app.services import evaluation_service, challenge_service, roadmap_service, question_service
import json

router = APIRouter()
ROUND_1_QUESTION_COUNT = 5


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


def safe_response(data, status_code=200):
    """Create a safe JSON response with UTF-8 encoding"""
    try:
        # Ensure all strings in data are ASCII-safe
        safe_data = _make_ascii_safe(data)
        json_str = json.dumps(safe_data, ensure_ascii=True, default=str)
    except Exception as internal_error:
        json_str = '{"success":true,"error":"serialization_failed"}'
    return Response(
        content=json_str.encode('utf-8'),
        status_code=status_code,
        media_type="application/json; charset=utf-8"
    )


def _make_ascii_safe(obj):
    """Recursively make all strings ASCII-safe"""
    if isinstance(obj, dict):
        return {k: _make_ascii_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_ascii_safe(item) for item in obj]
    elif isinstance(obj, str):
        # Replace any non-ASCII characters
        return obj.encode('ascii', errors='replace').decode('ascii')
    else:
        return obj


def safe_error_response(message="An error occurred", status_code=500):
    """Create a safe error response - only ASCII characters"""
    # Force ASCII-only message to avoid encoding issues
    ascii_message = message.encode('ascii', errors='replace').decode('ascii')
    return safe_response({"detail": ascii_message}, status_code)


@router.post("/generate-questions")
async def generate_questions(http_request: Request):
    """Generate exactly 5 questions for Round 1 - using raw Request to avoid Pydantic encoding issues"""
    try:
        # Read raw bytes first to avoid any JSON parsing issues
        body_bytes = await http_request.body()
        body_str = body_bytes.decode('utf-8')
        body = json.loads(body_str)
        topic = body.get("topic", "General")

        questions = await question_service.generate_questions(topic, difficulty="beginner")
        questions = questions[:ROUND_1_QUESTION_COUNT]
        return safe_response({"questions": questions, "round": 1, "total_questions": len(questions)})
    except Exception as e:
        # Write error to file for debugging
        with open('/tmp/error.log', 'w') as f:
            import traceback
            traceback.print_exc(file=f)
            f.write(f"\n\nException type: {type(e).__name__}\n")
            f.write(f"Exception str: {repr(str(e))}\n")
        return safe_error_response("Failed to generate questions")


@router.post("/submit-round-1")
async def submit_round_1(request: Round1SubmissionRequest):
    """Submit Round 1 answers and evaluate"""
    try:
        from app.models.schemas import QuestionAnswer
        questions_list = [
            QuestionAnswer(**q) if isinstance(q, dict) else q
            for q in request.questions
        ]
        analysis_request = LearningAnalysisRequest(
            student_name=request.student_name,
            topic=request.topic,
            questions=questions_list
        )

        # Evaluate Round 1
        evaluation = await evaluation_service.evaluate_learning(analysis_request)
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        weak_areas = evaluation.get("weak_areas", [])
        level = evaluation.get("level", "Beginner")

        # Generate roadmap
        roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas)
        roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

        if score < 50:
            # Generate beginner explanation
            content = await challenge_service.generate_beginner_explanation(request.topic, weak_areas)
            generated_content = {"type": "beginner_explanation", "content": content}

            return safe_response({
                "status": "completed",
                "round": 1,
                "evaluation": evaluation,
                "generated_content": generated_content,
                "roadmap": roadmap,
                "can_proceed_to_round_2": False
            })
        else:
            # Proceed to Round 2
            return safe_response({
                "status": "proceed_to_round_2",
                "round": 1,
                "score": score,
                "evaluation": evaluation,
                "can_proceed_to_round_2": True
            })
    except Exception as e:
        return safe_error_response("Failed to submit Round 1")


@router.post("/generate-round-2-questions")
async def generate_round_2_questions(request: TopicRequest):
    """Generate advanced challenge questions for Round 2"""
    try:
        questions = await question_service.generate_questions(request.topic, difficulty="advanced")
        return safe_response({"questions": questions, "round": 2, "total_questions": len(questions)})
    except Exception as e:
        return safe_error_response("Failed to generate Round 2 questions")


@router.post("/submit-round-2")
async def submit_round_2(request: Round2SubmissionRequest):
    """Submit Round 2 answers and provide detailed analysis"""
    try:
        from app.models.schemas import QuestionAnswer
        questions_list = [
            QuestionAnswer(**q) if isinstance(q, dict) else q
            for q in request.questions
        ]
        analysis_request = LearningAnalysisRequest(
            student_name=request.student_name,
            topic=request.topic,
            questions=questions_list
        )

        # Evaluate Round 2
        evaluation = await evaluation_service.evaluate_learning(analysis_request)
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        weak_areas = evaluation.get("weak_areas", [])
        level = evaluation.get("level", "Advanced")

        # Generate advanced insights
        content = await challenge_service.generate_advanced_challenges(request.topic, strengths)
        generated_content = {"type": "advanced_insights", "content": content}

        # Generate roadmap
        roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas)
        roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

        return safe_response({
            "status": "completed",
            "round": 2,
            "round_1_score": request.round_1_score,
            "round_2_evaluation": evaluation,
            "generated_content": generated_content,
            "roadmap": roadmap
        })
    except Exception as e:
        return safe_error_response("Failed to submit Round 2")


@router.post("/analyze-learning")
async def analyze_learning(request: LearningAnalysisRequest):
    """Legacy endpoint for backwards compatibility"""
    try:
        evaluation = await evaluation_service.evaluate_learning(request)
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        weak_areas = evaluation.get("weak_areas", [])
        level = evaluation.get("level", "Beginner")

        generated_content = {}
        if score < 50:
            content = await challenge_service.generate_beginner_explanation(request.topic, weak_areas)
            generated_content = {"type": "beginner_explanation", "content": content}
        else:
            content = await challenge_service.generate_advanced_challenges(request.topic, strengths)
            generated_content = {"type": "advanced_challenges", "content": content}

        roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas)
        roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

        return safe_response({
            "evaluation": evaluation,
            "generated_content": generated_content,
            "roadmap": roadmap,
        })
    except Exception as e:
        return safe_error_response("Failed to analyze learning")


@router.post("/submit-round-1")
async def submit_round_1(request: Round1SubmissionRequest):
    """
    Submit Round 1 answers and evaluate.
    Returns score and determines if user moves to Round 2 or gets results.
    """
    try:
        # Create a LearningAnalysisRequest for evaluation
        from app.models.schemas import QuestionAnswer
        questions_list = [
            QuestionAnswer(**q) if isinstance(q, dict) else q
            for q in request.questions
        ]
        analysis_request = LearningAnalysisRequest(
            student_name=request.student_name,
            topic=request.topic,
            questions=questions_list
        )

        # LLM CALL 1: Evaluate learner quiz answers
        evaluation = await evaluation_service.evaluate_learning(analysis_request)
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        weak_areas = evaluation.get("weak_areas", [])
        level = evaluation.get("level", "Beginner")

        # LLM CALL 3: Always generate roadmap
        roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas)
        roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

        if score < 50:
            # User scores below 50% - show results page with beginner explanation
            # LLM CALL 2: Generate beginner-friendly explanation
            content = await challenge_service.generate_beginner_explanation(request.topic, weak_areas)
            generated_content = {"type": "beginner_explanation", "content": content}

            return {
                "status": "completed",
                "round": 1,
                "evaluation": evaluation,
                "generated_content": generated_content,
                "roadmap": roadmap,
                "can_proceed_to_round_2": False
            }
        else:
            # User scores 50% or above - proceed to Round 2
            return {
                "status": "proceed_to_round_2",
                "round": 1,
                "score": score,
                "evaluation": evaluation,
                "can_proceed_to_round_2": True
            }
    except Exception as e:
        pass
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/generate-round-2-questions")
async def generate_round_2_questions(request: TopicRequest):
    """Generate advanced challenge questions for Round 2"""
    try:
        questions = await question_service.generate_questions(request.topic, difficulty="advanced")
        return {"questions": questions, "round": 2, "total_questions": len(questions)}
    except Exception as e:
        pass
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-round-2")
async def submit_round_2(request: Round2SubmissionRequest):
    """
    Submit Round 2 answers and provide detailed analysis with roadmap.
    """
    try:
        # Create a LearningAnalysisRequest for evaluation
        from app.models.schemas import QuestionAnswer
        questions_list = [
            QuestionAnswer(**q) if isinstance(q, dict) else q
            for q in request.questions
        ]
        analysis_request = LearningAnalysisRequest(
            student_name=request.student_name,
            topic=request.topic,
            questions=questions_list
        )

        # LLM CALL 1: Evaluate Round 2 answers
        evaluation = await evaluation_service.evaluate_learning(analysis_request)
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        weak_areas = evaluation.get("weak_areas", [])
        level = evaluation.get("level", "Advanced")

        # LLM CALL 2: Generate advanced insights or further challenges
        content = await challenge_service.generate_advanced_challenges(request.topic, strengths)
        generated_content = {"type": "advanced_insights", "content": content}

        # LLM CALL 3: Generate updated personalized learning roadmap
        roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas)
        roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

        return {
            "status": "completed",
            "round": 2,
            "round_1_score": request.round_1_score,
            "round_2_evaluation": evaluation,
            "generated_content": generated_content,
            "roadmap": roadmap
        }
    except Exception as e:
        pass
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-learning")
async def analyze_learning(request: LearningAnalysisRequest):
    """Legacy endpoint - kept for backwards compatibility"""
    try:
        # LLM Call 1: Evaluate learner quiz answers
        evaluation = await evaluation_service.evaluate_learning(request)
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        weak_areas = evaluation.get("weak_areas", [])
        level = evaluation.get("level", "Beginner")

        # IF/ELSE CONDITION
        generated_content = {}
        if score < 50:
            # LLM CALL 2: Generate beginner-friendly explanation
            content = await challenge_service.generate_beginner_explanation(request.topic, weak_areas)
            generated_content = {"type": "beginner_explanation", "content": content}
        else:
            # LLM CALL 2: Generate advanced challenge problems
            content = await challenge_service.generate_advanced_challenges(request.topic, strengths)
            generated_content = {"type": "advanced_challenges", "content": content}

        # LLM CALL 3: Generate personalized learning roadmap
        roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas)
        roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

        return {
            "evaluation": evaluation,
            "generated_content": generated_content,
            "roadmap": roadmap,
        }
    except Exception as e:
        pass
        raise HTTPException(status_code=500, detail=str(e))
