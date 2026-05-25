import json
from app.services.huggingface_service import query_model
from app.utils.prompts import QUESTION_GENERATION_PROMPT


async def generate_questions(topic: str, num_questions: int = 5, difficulty: str = "beginner"):
    """
    Generates quiz questions for a given topic using an LLM.
    Returns a list of MCQ questions with options and correct answers.

    Args:
        topic: The topic for question generation
        num_questions: Number of questions to generate (default 5)
        difficulty: Level of difficulty - "beginner", "intermediate", or "advanced"
    """
    prompt = QUESTION_GENERATION_PROMPT.format(topic=topic, difficulty=difficulty)

    try:
        response = await query_model(prompt)
        # The response from the model is often a list with one item
        if isinstance(response, list) and len(response) > 0:
            generated_text = response[0].get('generated_text', '[]')

            # The model might return the prompt in the response, so we need to find the JSON
            json_str_start = generated_text.find('[')
            json_str_end = generated_text.rfind(']') + 1

            if json_str_start != -1 and json_str_end > json_str_start:
                json_str = generated_text[json_str_start:json_str_end]
                questions_data = json.loads(json_str)
                return questions_data
            else:
                raise ValueError(f"No JSON array found in the model's response. Start: {json_str_start}, End: {json_str_end}")
        else:
            raise ValueError("Unexpected response format from the model.")

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON from the model's response: {e}")
    except Exception as e:
        raise e
