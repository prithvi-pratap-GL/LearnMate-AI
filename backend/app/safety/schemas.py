from dataclasses import dataclass
from typing import Optional


@dataclass
class SafetyCheckResult:
    is_safe: bool
    reason: Optional[str] = None
    sanitized_text: Optional[str] = None
    pii_detected: bool = False
    risk_score: float = 0.0