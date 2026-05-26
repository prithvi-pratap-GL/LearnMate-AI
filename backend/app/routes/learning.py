from fastapi import APIRouter, Request, HTTPException
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


@router.post("/generate-questions")
async def generate_questions(http_request: Request):
    """Generate exactly 5 questions for Round 1"""
    try:
        body_bytes = await http_request.body()
        body_str = body_bytes.decode('utf-8')
        body = json.loads(body_str)
        topic = body.get("topic", "General")

        questions = await question_service.generate_questions(topic, difficulty="beginner")
        questions = questions[:ROUND_1_QUESTION_COUNT]
        return {"questions": questions, "round": 1, "total_questions": len(questions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate questions")


@router.post("/submit-round-1")
async def submit_round_1(request: Round1SubmissionRequest):
    """
    Submit Round 1 answers and evaluate.
    Returns score and determines if user moves to Round 2 or gets results.
    """
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

        # Generate roadmap (one level higher than current)
        roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas, score, request.topic)
        roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

        if score < 50:
            # User scores below 50% - show results page with performance analysis
            questions_dict = [q.model_dump() if hasattr(q, 'model_dump') else q for q in questions_list]
            content = await challenge_service.generate_performance_analysis(request.topic, questions_dict, score)
            generated_content = {"type": "performance_analysis", "content": content}

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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-round-2-questions")
async def generate_round_2_questions(http_request: Request):
    """Generate advanced challenge questions for Round 2, excluding Round 1 questions"""
    try:
        body_bytes = await http_request.body()
        body_str = body_bytes.decode('utf-8')
        body = json.loads(body_str)
        topic = body.get("topic", "General")
        round_1_questions = body.get("round_1_questions", [])

        # Generate more advanced questions
        questions = await question_service.generate_questions(topic, difficulty="advanced")

        # Filter out any questions that were in Round 1
        round_1_q_texts = {q.get("question", "").lower() for q in round_1_questions}
        filtered_questions = [
            q for q in questions
            if q.get("question", "").lower() not in round_1_q_texts
        ]

        # If we filtered out too many, generate more to reach at least 5
        if len(filtered_questions) < 5:
            all_questions = filtered_questions
            attempts = 0
            while len(all_questions) < 5 and attempts < 3:
                more_questions = await question_service.generate_questions(topic, difficulty="advanced")
                for q in more_questions:
                    if q.get("question", "").lower() not in round_1_q_texts and q not in all_questions:
                        all_questions.append(q)
                        if len(all_questions) >= 5:
                            break
                attempts += 1
            filtered_questions = all_questions[:5]

        return {"questions": filtered_questions[:5], "round": 2, "total_questions": len(filtered_questions[:5])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-round-2")
async def submit_round_2(request: Round2SubmissionRequest):
    """
    Submit Round 2 answers and provide detailed analysis with roadmap.
    """
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

        # Generate solution explanations
        questions_dict = [q.model_dump() if hasattr(q, 'model_dump') else q for q in questions_list]
        content = await challenge_service.generate_solution_explanation(request.topic, questions_dict, score)
        generated_content = {"type": "solution", "content": content}

        # Generate roadmap (one level higher than current)
        roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas, score, request.topic)
        roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

        return {
            "status": "completed",
            "round": 2,
            "round_1_score": request.round_1_score,
            "round_2_evaluation": evaluation,
            "generated_content": generated_content,
            "roadmap": roadmap,
            "questions": questions_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            questions_dict = [q.model_dump() if hasattr(q, 'model_dump') else q for q in questions_list]
            content = await challenge_service.generate_performance_analysis(request.topic, questions_dict, score)
            generated_content = {"type": "performance_analysis", "content": content}
        else:
            content = await challenge_service.generate_advanced_challenges(request.topic, strengths, score, level)
            generated_content = {"type": "advanced_challenges", "content": content}

        roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas, score, request.topic)
        roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

        return {
            "evaluation": evaluation,
            "generated_content": generated_content,
            "roadmap": roadmap,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
