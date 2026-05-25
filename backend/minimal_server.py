#!/usr/bin/env python
"""
Minimal async server without FastAPI to avoid encoding issues
"""
import asyncio
import json
import sys
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

from app.services.question_service import generate_questions
from app.services.evaluation_service import evaluate_learning
from app.services.challenge_service import generate_beginner_explanation, generate_advanced_challenges
from app.services.roadmap_service import generate_roadmap
from app.models.schemas import LearningAnalysisRequest, QuestionAnswer


async def handle_generate_questions(topic):
    """Generate questions endpoint"""
    try:
        questions = await generate_questions(topic, difficulty="beginner")
        questions = questions[:5]
        return {
            "questions": questions,
            "round": 1,
            "total_questions": len(questions)
        }
    except Exception as e:
        return {"error": "Failed to generate questions"}


async def handle_submit_round_1(student_name, topic, questions_data):
    """Handle Round 1 submission"""
    try:
        questions_list = [
            QuestionAnswer(**q) if isinstance(q, dict) else q
            for q in questions_data
        ]
        request = LearningAnalysisRequest(
            student_name=student_name,
            topic=topic,
            questions=questions_list
        )

        evaluation = await evaluate_learning(request)
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        weak_areas = evaluation.get("weak_areas", [])
        level = evaluation.get("level", "Beginner")

        roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas)
        roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

        if score < 50:
            content = await generate_beginner_explanation(topic, weak_areas)
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
            return {
                "status": "proceed_to_round_2",
                "round": 1,
                "score": score,
                "evaluation": evaluation,
                "can_proceed_to_round_2": True
            }
    except Exception as e:
        return {"error": "Failed to evaluate"}


if __name__ == "__main__":
    from aiohttp import web

    async def generate_questions_handler(request):
        """HTTP handler for generating questions"""
        try:
            data = await request.json()
            topic = data.get("topic", "General")
            result = await handle_generate_questions(topic)
            return web.json_response(result)
        except Exception as e:
            return web.json_response({"error": "Invalid request"}, status=400)

    async def submit_round_1_handler(request):
        """HTTP handler for Round 1 submission"""
        try:
            data = await request.json()
            result = await handle_submit_round_1(
                data.get("student_name"),
                data.get("topic"),
                data.get("questions", [])
            )
            return web.json_response(result)
        except Exception as e:
            return web.json_response({"error": "Invalid request"}, status=400)

    async def health_handler(request):
        """Health check"""
        return web.json_response({"message": "LearnMate AI Backend is running"})

    # Create app
    app = web.Application()
    app.router.add_post('/api/generate-questions', generate_questions_handler)
    app.router.add_post('/api/submit-round-1', submit_round_1_handler)
    app.router.add_get('/', health_handler)

    print("Starting minimal server on http://127.0.0.1:5000")
    web.run_app(app, host='127.0.0.1', port=5000, print=None)
