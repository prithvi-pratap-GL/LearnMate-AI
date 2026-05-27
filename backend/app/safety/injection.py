import re
from transformers import pipeline
from app.config.settings import settings

classifier = pipeline(
    "text-classification",
    model="ProtectAI/deberta-v3-base-prompt-injection-v2",
)

# Fast heuristic layer
SUSPICIOUS_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"reveal\s+(system|hidden)\s+prompt",
    r"act\s+as",
    r"jailbreak",
    r"you\s+are\s+now",
    r"bypass\s+safety",
]


def check_injection(text: str):

    lower = text.lower()

    # 1. Regex layer first
    heuristic_hit = any(
        re.search(p, lower)
        for p in SUSPICIOUS_PATTERNS
    )

    # 2. Model layer
    result = classifier(text)[0]

    label = result["label"].upper()
    score = float(result["score"])

    # Production logic:
    # Require BOTH
    is_attack = (
        heuristic_hit
        and label == "INJECTION"
        and score >= settings.INJECTION_THRESHOLD
    )

    return not is_attack, score, text