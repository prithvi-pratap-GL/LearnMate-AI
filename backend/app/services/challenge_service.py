from app.services.huggingface_service import query_model
from app.utils.prompts import BEGINNER_EXPLANATION_PROMPT, ADVANCED_CHALLENGES_PROMPT

async def generate_beginner_explanation(topic: str, weak_areas: list):
    """
    Generates a beginner-friendly explanation for a given topic and weak areas.
    """
    prompt = BEGINNER_EXPLANATION_PROMPT.format(topic=topic, weak_areas=", ".join(weak_areas))
    try:
        response = await query_model(prompt)
        if isinstance(response, list) and len(response) > 0:
            return response[0].get('generated_text', '')
        return ''
    except Exception as e:
        raise Exception(f"Failed to generate beginner explanation: {e}")

async def generate_advanced_challenges(topic: str, strengths: list):
    """
    Generates advanced challenge problems for a given topic and strengths.
    """
    prompt = ADVANCED_CHALLENGES_PROMPT.format(topic=topic, strengths=", ".join(strengths))
    try:
        response = await query_model(prompt)
        if isinstance(response, list) and len(response) > 0:
            return response[0].get('generated_text', '')
        return ''
    except Exception as e:
        raise Exception(f"Failed to generate advanced challenges: {e}")
