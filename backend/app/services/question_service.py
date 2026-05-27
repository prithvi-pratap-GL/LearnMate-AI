import json
from app.services.huggingface_service import query_model
from app.utils.prompts import QUESTION_GENERATION_PROMPT
from pydantic import BaseModel, ValidationError
from typing import List


class MCQQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str


async def generate_questions(
    topic: str, num_questions: int = 5, difficulty: str = "beginner"
):
    """
    Generates quiz questions using LLM.
    Validates with Pydantic.
    Retries once using correction prompt if schema fails.
    """

    base_prompt = QUESTION_GENERATION_PROMPT.format(topic=topic, difficulty=difficulty)

    prompt = base_prompt

    for attempt in range(2):

        try:

            response = await query_model(prompt)

            if not (isinstance(response, list) and len(response) > 0):
                raise ValueError("Unexpected response format.")

            generated_text = response[0].get("generated_text", "[]")

            print("\n===== RAW MODEL OUTPUT =====\n")
            print(generated_text)
            print("\n============================\n")

            json_start = generated_text.find("[")
            json_end = generated_text.rfind("]") + 1

            if json_start == -1 or json_end <= json_start:
                raise ValueError("No JSON array found.")

            json_str = generated_text[json_start:json_end]

            questions_data = json.loads(json_str)

            validated_questions = [
                MCQQuestion(**q).model_dump() for q in questions_data
            ]

            return validated_questions

        except (json.JSONDecodeError, ValidationError, ValueError) as e:

            print(f"[VALIDATION ERROR] Attempt {attempt+1}: {e}")

            if attempt == 0:

                prompt = f"""
Your previous response was INVALID JSON.

Error:
{str(e)}

You MUST follow these rules strictly:

1. Return ONLY valid JSON
2. No markdown
3. No explanation
4. No surrounding text
5. "options" MUST be an array of EXACTLY 4 STRINGS
6. Every option must be quoted
7. Escape internal quotation marks
8. Output must begin with [ and end with ]

Required schema:

[
  {{
    "question": "string",
    "options": [
      "string",
      "string",
      "string",
      "string"
    ],
    "correct_answer": "string"
  }}
]

Example valid format:

[
  {{
    "question": "What is AI?",
    "options": [
      "Artificial Intelligence",
      "Machine Learning",
      "Database",
      "Compiler"
    ],
    "correct_answer": "Artificial Intelligence"
  }}
]

Now regenerate the FULL response.

Original task:

{base_prompt}
"""

                continue

            raise ValueError(f"Question generation failed after retry: {e}")

        except Exception as e:
            raise e
