import logging

from app.config.settings import settings
from .schemas import SafetyCheckResult
from .pii import redact_pii
from .toxicity import check_toxicity
from .injection import check_injection
from .policies import check_policy

log = logging.getLogger(__name__)


class SafetyGateway:

    @staticmethod
    def validate_input(text: str):

        # Injection
        if settings.ENABLE_INJECTION:
            valid, risk, sanitized = check_injection(
                text
            )

            if not valid:
                log.warning(
                    "Prompt injection blocked"
                )
                return SafetyCheckResult(
                    False,
                    "Prompt injection detected.",
                    risk_score=risk,
                )
        else:
            sanitized = text

        # Toxicity
        if settings.ENABLE_TOXICITY:
            safe, risk = check_toxicity(
                sanitized
            )

            if not safe:
                log.warning(
                    "Toxic content blocked"
                )

                return SafetyCheckResult(
                    False,
                    "Unsafe or harmful content detected.",
                    risk_score=risk,
                )

        # Policy
        if settings.ENABLE_POLICY:
            allowed, reason = check_policy(
                sanitized
            )

            if not allowed:
                return SafetyCheckResult(
                    False,
                    reason
                )

        # PII
        pii_found = False

        if settings.ENABLE_PII:
            sanitized, pii_found = redact_pii(
                sanitized
            )

        return SafetyCheckResult(
            True,
            sanitized_text=sanitized,
            pii_detected=pii_found,
        )

    @staticmethod
    def validate_output(text: str):

        if settings.ENABLE_TOXICITY:
            safe, risk = check_toxicity(text)

            if not safe:
                return SafetyCheckResult(
                    False,
                    "Generated output blocked.",
                    risk_score=risk,
                )

        pii_found = False

        if settings.ENABLE_PII:
            text, pii_found = redact_pii(text)

        return SafetyCheckResult(
            True,
            sanitized_text=text,
            pii_detected=pii_found,
        )