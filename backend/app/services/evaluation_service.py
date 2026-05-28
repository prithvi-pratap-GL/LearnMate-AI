import json
import logging

from app.services.judge_service import (
    judge_answer,
)
from app.services.huggingface_service import (
    query_model,
)
from app.utils.prompts import (
    EVALUATION_PROMPT,
)
from app.models.schemas import (
    LearningAnalysisRequest,
)

log = logging.getLogger(__name__)

# Evaluation model preference order - HuggingFace Router compatible
EVALUATION_MODELS = [
    "meta-llama/Llama-3.1-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "meta-llama/Llama-2-70b-chat-hf",
]


async def evaluate_learning(
    request: LearningAnalysisRequest,
    model_index: int = 0,
):
    """
    Evaluate learner answers using:

    LLM Judge
    +
    Multi-model failover
    """

    questions_list = [
        {
            "question": q.question,
            "student_answer": q.student_answer,
            "correct_answer": q.correct_answer,
        }
        for q in request.questions
    ]

    # -------------------------
    # LLM Judge Scoring
    # -------------------------

    judgements = []

    for q in questions_list:

        try:

            result = await judge_answer(
                q["question"],
                q["student_answer"],
                q["correct_answer"],
            )

            judgements.append(result)

        except Exception as e:

            log.warning("[JUDGE FAILED] " f"{e}")

            # safe fallback
            judgements.append(
                {
                    "correct": False,
                    "score": 0,
                    "reason": "Judge unavailable",
                }
            )

    correct_count = sum(1 for j in judgements if j.get("correct", False))
    total_questions = len(judgements)
    score_percentage = int((correct_count / total_questions * 100) if total_questions > 0 else 0)

    answers_json = json.dumps(
        questions_list,
        ensure_ascii=False,
    )

    answers_str = f"Score: {score_percentage}%\n\n" f"{answers_json}"

    prompt = EVALUATION_PROMPT.format(
        topic=request.topic,
        answers=answers_str,
    )

    candidate_models = EVALUATION_MODELS[model_index:] + EVALUATION_MODELS[:model_index]

    last_error = None

    # -------------------------
    # Evaluation LLM
    # -------------------------

    for model in candidate_models:

        try:

            log.info(f"[EVAL] Trying " f"{model}")

            response = await query_model(
                prompt,
                model=model,
            )

            is_mock = False

            if isinstance(
                response,
                dict,
            ) and response.get("mock"):
                is_mock = True
                response = response["data"]

            if not (
                isinstance(
                    response,
                    list,
                )
                and len(response) > 0
            ):
                raise ValueError("Unexpected " "response format.")

            generated_text = response[0].get(
                "generated_text",
                "{}",
            )

            print("\n===== " "EVALUATION " "RAW OUTPUT " "=====\n")
            print(generated_text)
            print("\n==========" "===========\n")

            json_start = generated_text.find("{")

            json_end = generated_text.rfind("}") + 1

            if json_start == -1 or json_end <= json_start:
                raise ValueError("No JSON " "object found.")

            json_str = generated_text[json_start:json_end]

            evaluation_data = json.loads(json_str)

            # ------------------
            # enrich response
            # ------------------

            evaluation_data["score"] = score_percentage

            evaluation_data["judgements"] = judgements

            evaluation_data["source"] = "mock" if is_mock else "llm"

            evaluation_data["evaluation_model"] = model

            log.info("[EVAL] Success " f"using {model}")

            return evaluation_data

        except (
            json.JSONDecodeError,
            ValueError,
        ) as e:

            log.warning("[EVAL PARSE FAILED] " f"{model}: {e}")

            last_error = e
            continue

        except Exception as e:

            log.warning("[EVAL MODEL FAILED] " f"{model}: {e}")

            last_error = e
            continue

    raise RuntimeError(
        "All evaluation " "models failed. " f"Last error: " f"{last_error}"
    )
