import json
from json import JSONDecoder
from typing import List

from json_repair import repair_json
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
)

from app.services.huggingface_service import (
    query_model,
)
from app.utils.prompts import (
    QUESTION_GENERATION_PROMPT,
)


class MCQQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str

    @field_validator("question")
    @classmethod
    def validate_question(
        cls,
        value,
    ):
        if len(value.strip()) < 10:
            raise ValueError("Question too short.")
        return value

    @field_validator("options")
    @classmethod
    def validate_options(
        cls,
        value,
    ):
        if len(value) != 4:
            raise ValueError("Exactly 4 options required.")

        if len(set(value)) != 4:
            raise ValueError("Duplicate options found.")

        for option in value:
            if len(option.strip()) < 2:
                raise ValueError("Invalid option text.")

        return value

    @field_validator("correct_answer")
    @classmethod
    def validate_answer(
        cls,
        value,
        info,
    ):
        options = info.data.get("options") if info.data else []

        if options and value not in options:
            raise ValueError("Correct answer must exist " "inside options.")

        return value


async def generate_questions(
    topic: str,
    num_questions: int = 5,
    difficulty: str = "beginner",
):
    """
    Generate quiz questions using LLM.

    Pipeline:

    LLM
    ↓
    raw_decode
    ↓
    json_repair fallback
    ↓
    normalize repaired output
    ↓
    Pydantic validation
    ↓
    correction retry
    ↓
    validated questions
    """

    base_prompt = QUESTION_GENERATION_PROMPT.format(
        topic=topic,
        difficulty=difficulty,
    )

    prompt = base_prompt

    # initial attempt + one correction retry
    for attempt in range(2):

        try:

            response = await query_model(prompt)

            is_mock = False

            if isinstance(response, dict) and response.get("mock"):
                is_mock = True
                response = response["data"]

            if not (isinstance(response, list) and len(response) > 0):
                raise ValueError("Unexpected response format.")

            generated_text = response[0].get(
                "generated_text",
                "[]",
            )

            print("\n===== RAW MODEL OUTPUT =====\n")
            print(generated_text)
            print("\n============================\n")

            json_start = generated_text.find("[")

            if json_start == -1:
                raise ValueError("No JSON array found.")

            extracted = generated_text[json_start:]

            decoder = JSONDecoder()

            # First parse attempt
            try:

                questions_data, end_idx = decoder.raw_decode(extracted)

            except json.JSONDecodeError:

                print("[JSON REPAIR] " "Attempting repair...")

                repaired = repair_json(extracted)

                print("\n===== REPAIRED JSON =====\n")
                print(repaired)
                print("\n=========================\n")

                questions_data = json.loads(repaired)

            # normalize repaired output
            normalized_questions = []

            if not isinstance(
                questions_data,
                list,
            ):
                raise ValueError("Expected JSON array.")

            for item in questions_data:

                # repair_json may create nested arrays
                if isinstance(
                    item,
                    list,
                ):
                    normalized_questions.extend(item)

                elif isinstance(
                    item,
                    dict,
                ):
                    normalized_questions.append(item)

            # keep only dicts
            normalized_questions = [
                q
                for q in normalized_questions
                if isinstance(
                    q,
                    dict,
                )
            ]

            if not (normalized_questions):
                raise ValueError("No valid question " "objects found.")

            validated_questions = []

            # validate individually
            for q in normalized_questions:

                try:

                    validated = MCQQuestion(**q).model_dump()

                    validated_questions.append(validated)

                except ValidationError as e:

                    print("\n[QUESTION SKIPPED]\n")
                    print(e)

                    continue

            if len(validated_questions) == 0:
                raise ValueError("No valid questions " "after validation.")

            # trim to requested count
            validated_questions = validated_questions[:num_questions]

            # minimum viable output
            minimum_required = max(
                3,
                num_questions // 2,
            )

            if len(validated_questions) < minimum_required:
                raise ValueError("Too few valid " "questions.")

            return {
                "questions": validated_questions,
                "source": (
                    "mock"
                    if is_mock
                    else "llm"
                ),
            }

        except (
            json.JSONDecodeError,
            ValidationError,
            ValueError,
        ) as e:

            print(f"\n[VALIDATION ERROR] " f"Attempt " f"{attempt+1}: {e}\n")

            # retry once
            if attempt == 0:

                prompt = f"""
Your previous response was INVALID.

Error:
{str(e)}

You MUST follow these rules STRICTLY:

1. Return ONLY valid JSON
2. No markdown
3. No explanations
4. No surrounding text
5. Output MUST begin with [
6. Output MUST end with ]
7. Exactly {num_questions} questions
8. Each question MUST contain:

- question
- options
- correct_answer

9. "options" MUST contain EXACTLY 4 FULL STRINGS
10. No duplicate options
11. correct_answer MUST match one option EXACTLY
12. No duplicate keys
13. No nested arrays
14. Escape quotation marks properly
15. Do NOT abbreviate options
16. Do NOT split strings across lines

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

Example:

[
  {{
    "question":
      "What is AI?",
    "options": [
      "Artificial Intelligence",
      "Machine Learning",
      "Database",
      "Compiler"
    ],
    "correct_answer":
      "Artificial Intelligence"
  }}
]

Regenerate the FULL response.

Original task:

{base_prompt}
"""

                continue

            raise ValueError("Question generation " f"failed after retry: {e}")

        except Exception as e:
            raise e
