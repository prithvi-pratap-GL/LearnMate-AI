import json
import logging

from app.services.huggingface_service import (
    query_model,
    calculate_score_from_answers,
)
from app.utils.prompts import EVALUATION_PROMPT
from app.models.schemas import LearningAnalysisRequest

log = logging.getLogger(__name__)

# Evaluation model preference order
EVALUATION_MODELS = [
    "meta-llama/Llama-2-70b-chat-hf",
    "mistralai/Mistral-Large-Instruct-2407",
    "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
    "mistralai/Mistral-7B-Instruct-v0.2",
]


async def evaluate_learning(
    request: LearningAnalysisRequest,
    model_index: int = 0,
):
    """
    Evaluate learner answers using multi-model failover.

    Flow:
    Preferred model
        ↓
    Fail?
        ↓
    Try next model
        ↓
    Parse JSON
        ↓
    Return evaluation
    """

    # Prepare answer payload
    questions_list = [
        {
            "question": q.question,
            "student_answer": q.student_answer,
            "correct_answer": q.correct_answer,
        }
        for q in request.questions
    ]

    # Deterministic scoring
    score = calculate_score_from_answers(questions_list)

    answers_json = json.dumps(
        questions_list,
        ensure_ascii=False,
    )

    answers_str = f"Score: {score}\n\n" f"{answers_json}"

    prompt = EVALUATION_PROMPT.format(
        topic=request.topic,
        answers=answers_str,
    )

    # Start from preferred model index
    candidate_models = EVALUATION_MODELS[model_index:] + EVALUATION_MODELS[:model_index]

    last_error = None

    for model in candidate_models:

        try:

            log.info(f"[EVAL] Trying model: {model}")

            response = await query_model(
                prompt,
                model=model,
            )

            if not (isinstance(response, list) and len(response) > 0):
                raise ValueError("Unexpected response format.")

            generated_text = response[0].get(
                "generated_text",
                "{}",
            )

            print("\n===== EVALUATION RAW OUTPUT =====\n")
            print(generated_text)
            print("\n===============================\n")

            # safer extraction
            json_start = generated_text.find("{")
            json_end = generated_text.rfind("}") + 1

            if json_start == -1 or json_end <= json_start:
                raise ValueError("No JSON object found.")

            json_str = generated_text[json_start:json_end]

            evaluation_data = json.loads(json_str)

            # authoritative score
            evaluation_data["score"] = score

            log.info(f"[EVAL] Success using {model}")

            return evaluation_data

        except (
            json.JSONDecodeError,
            ValueError,
        ) as e:

            log.warning(f"[EVAL] Parse failed " f"for {model}: {e}")

            last_error = e
            continue

        except Exception as e:

            log.warning(f"[EVAL] Model failed " f"{model}: {e}")

            last_error = e
            continue

    raise RuntimeError("All evaluation models failed. " f"Last error: {last_error}")
