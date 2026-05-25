"""
Test script to verify all LLM calls are working correctly.
Run this from the backend directory: python test_llm_calls.py
"""
import asyncio
import json
from app.services import question_service, evaluation_service, challenge_service, roadmap_service
from app.models.schemas import LearningAnalysisRequest, QuestionAnswer

async def test_llm_calls():
    print("=" * 60)
    print("Testing LLM Calls for LearnMate AI")
    print("=" * 60)

    # Test LLM CALL 0: Question Generation
    print("\n[0] Testing Question Generation...")
    try:
        questions = await question_service.generate_questions("Python Programming")
        print("[OK] LLM CALL 0 Success!")
        print(f"Generated {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q.get('question', 'N/A')[:60]}...")
    except Exception as e:
        print(f"[FAIL] LLM CALL 0 Failed: {e}")
        return

    # Test LLM CALL 1: Evaluation
    print("\n[1] Testing Evaluation...")
    try:
        test_questions = [
            QuestionAnswer(
                question="What is a list in Python?",
                correct_answer="An ordered collection of items",
                student_answer="A collection of data"
            ),
            QuestionAnswer(
                question="What does len() do?",
                correct_answer="Returns the length of an object",
                student_answer="Returns the size"
            )
        ]
        request = LearningAnalysisRequest(
            student_name="Test Student",
            topic="Python Programming",
            questions=test_questions
        )
        evaluation = await evaluation_service.evaluate_learning(request)
        print("[OK] LLM CALL 1 Success!")
        print(f"  Score: {evaluation.get('score')}%")
        print(f"  Level: {evaluation.get('level')}")
        print(f"  Strengths: {evaluation.get('strengths')}")
        print(f"  Weak Areas: {evaluation.get('weak_areas')}")

        score = evaluation.get('score', 0)
        strengths = evaluation.get('strengths', [])
        weak_areas = evaluation.get('weak_areas', [])
        level = evaluation.get('level', 'Beginner')
    except Exception as e:
        print(f"[FAIL] LLM CALL 1 Failed: {e}")
        return

    # Test LLM CALL 2: Conditional generation based on score
    if score < 50:
        print("\n[2A] Testing Beginner Explanation (score < 50)...")
        try:
            content = await challenge_service.generate_beginner_explanation("Python Programming", weak_areas)
            print("[OK] LLM CALL 2A Success!")
            print(f"  Content preview: {content[:200]}...")
        except Exception as e:
            print(f"[FAIL] LLM CALL 2A Failed: {e}")
    else:
        print("\n[2B] Testing Advanced Challenges (score >= 50)...")
        try:
            content = await challenge_service.generate_advanced_challenges("Python Programming", strengths)
            print("[OK] LLM CALL 2B Success!")
            print(f"  Content preview: {content[:200]}...")
        except Exception as e:
            print(f"[FAIL] LLM CALL 2B Failed: {e}")

    # Test LLM CALL 3: Roadmap Generation
    print("\n[3] Testing Personalized Roadmap...")
    try:
        roadmap = await roadmap_service.generate_roadmap(level, strengths, weak_areas)
        print("[OK] LLM CALL 3 Success!")
        print(f"  Roadmap preview: {roadmap[:200]}...")
    except Exception as e:
        print(f"[FAIL] LLM CALL 3 Failed: {e}")

    print("\n" + "=" * 60)
    print("All LLM Calls Test Completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_llm_calls())
