import json
import difflib
from json import JSONDecoder

from app.services.huggingface_service import query_model
from app.utils.prompts import LLM_JUDGE_PROMPT


def similarity(
    a: str,
    b: str,
):
    return difflib.SequenceMatcher(
        None,
        a.lower().strip(),
        b.lower().strip(),
    ).ratio()


async def judge_answer(
    question: str,
    student_answer: str,
    correct_answer: str,
):
    """
    Hybrid judge.

    Exact
    ↓
    Similarity
    ↓
    LLM fallback
    """

    student = (student_answer or "").strip()

    correct = (correct_answer or "").strip()

    # ------------------
    # Tier 1
    # Exact match
    # ------------------

    if student.lower() == correct.lower():
        return {
            "correct": True,
            "score": 10,
            "reason": "Exact match",
            "judge": "deterministic",
        }

    # ------------------
    # Tier 2
    # Similarity
    # ------------------

    sim = similarity(
        student,
        correct,
    )

    if sim >= 0.80:

        return {
            "correct": True,
            "score": 10,
            "reason": "Semantically similar",
            "judge": "similarity",
        }

    # ------------------
    # Tier 3
    # LLM Judge
    # ------------------

    prompt = LLM_JUDGE_PROMPT.format(
        question=question,
        student_answer=student,
        correct_answer=correct,
    )

    response = await query_model(prompt)

    if isinstance(response, dict) and response.get("mock"):
        response = response["data"]

    if not (isinstance(response, list) and len(response) > 0):
        raise ValueError("Judge response invalid")

    generated = response[0].get(
        "generated_text",
        "{}",
    )

    print("\n===== JUDGE OUTPUT =====\n")
    print(generated)
    print("\n========================\n")

    start = generated.find("{")

    if start == -1:
        raise ValueError("No judge JSON")

    decoder = JSONDecoder()

    judgement, _ = decoder.raw_decode(generated[start:])

    judgement["judge"] = "llm"

    return judgement
