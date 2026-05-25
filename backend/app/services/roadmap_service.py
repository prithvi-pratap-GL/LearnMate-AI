from app.services.huggingface_service import query_model
from app.utils.prompts import ROADMAP_PROMPT

async def generate_roadmap(level: str, strengths: list, weak_areas: list, score: int = 50, topic: str = ""):
    """
    Generates a personalized learning roadmap at one level higher than current level.
    Beginner → Intermediate, Intermediate → Advanced, Advanced → Expert
    """
    # Determine the target level (one step higher)
    level_hierarchy = {"Beginner": "Intermediate", "Intermediate": "Advanced", "Advanced": "Expert"}
    target_level = level_hierarchy.get(level, "Advanced")

    prompt = ROADMAP_PROMPT.format(
        topic=topic,
        level=target_level,
        strengths=", ".join(strengths),
        weak_areas=", ".join(weak_areas),
        score=score
    )
    try:
        response = await query_model(prompt)
        if isinstance(response, list) and len(response) > 0:
            return response[0].get('generated_text', '')
        return ''
    except Exception as e:
        raise Exception(f"Failed to generate roadmap: {e}")
