import re

DENY_PATTERNS = [
    r"\b(hack|hacking|exploit)\b",
    r"\b(ransomware|malware|virus)\b",
    r"\b(dark\s*web|tor)\b",
]


def check_policy(text: str):
    lower = text.lower()

    for pattern in DENY_PATTERNS:
        if re.search(pattern, lower):
            return (
                False,
                "This topic is outside allowed platform scope."
            )

    return True, None