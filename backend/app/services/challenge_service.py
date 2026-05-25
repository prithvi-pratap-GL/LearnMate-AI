from app.services.huggingface_service import query_model
from app.utils.prompts import PERFORMANCE_ANALYSIS_PROMPT, ADVANCED_CHALLENGES_PROMPT, SOLUTION_EXPLANATION_PROMPT
import json

async def generate_performance_analysis(topic: str, questions: list, score: int = 50):
    """
    Generates a detailed performance analysis of the learner's answers.
    Includes pointwise breakdown of answers and highlights strengths.
    """
    questions_json = json.dumps(questions)
    prompt = PERFORMANCE_ANALYSIS_PROMPT.format(topic=topic, questions=questions_json, score=score)
    try:
        response = await query_model(prompt)
        if isinstance(response, list) and len(response) > 0:
            return response[0].get('generated_text', '')
        return ''
    except Exception as e:
        raise Exception(f"Failed to generate performance analysis: {e}")

async def generate_advanced_challenges(topic: str, strengths: list, score: int = 75, level: str = "Advanced"):
    """
    Generates advanced challenge problems for a given topic and strengths.
    """
    prompt = ADVANCED_CHALLENGES_PROMPT.format(topic=topic, strengths=", ".join(strengths), score=score, level=level)
    try:
        response = await query_model(prompt)
        if isinstance(response, list) and len(response) > 0:
            return response[0].get('generated_text', '')
        return ''
    except Exception as e:
        raise Exception(f"Failed to generate advanced challenges: {e}")

async def generate_solution_explanation(topic: str, questions: list, score: int = 75):
    """
    Generates detailed explanations of correct answers for the given questions.
    """
    questions_json = json.dumps(questions)
    prompt = SOLUTION_EXPLANATION_PROMPT.format(topic=topic, questions=questions_json, score=score)
    try:
        response = await query_model(prompt)
        if isinstance(response, list) and len(response) > 0:
            return response[0].get('generated_text', '')
        return ''
    except Exception as e:
        raise Exception(f"Failed to generate solution explanation: {e}")
