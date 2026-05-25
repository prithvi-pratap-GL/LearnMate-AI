from app.services.huggingface_service import query_model
from app.utils.prompts import ROADMAP_PROMPT

async def generate_roadmap(level: str, strengths: list, weak_areas: list):
    """
    Generates a personalized learning roadmap.
    """
    prompt = ROADMAP_PROMPT.format(
        level=level,
        strengths=", ".join(strengths),
        weak_areas=", ".join(weak_areas)
    )
    try:
        response = await query_model(prompt)
        if isinstance(response, list) and len(response) > 0:
            return response[0].get('generated_text', '')
        return ''
    except Exception as e:
        raise Exception(f"Failed to generate roadmap: {e}")
