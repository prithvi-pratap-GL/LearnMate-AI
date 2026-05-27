from presidio_analyzer import (
    AnalyzerEngine,
    PatternRecognizer,
    Pattern,
)
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


# Aadhaar
aadhaar_pattern = Pattern(
    name="aadhaar",
    regex=r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    score=0.9,
)

aadhaar_recognizer = PatternRecognizer(
    supported_entity="AADHAAR",
    patterns=[aadhaar_pattern],
)

# PAN
pan_pattern = Pattern(
    name="pan",
    regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    score=0.9,
)

pan_recognizer = PatternRecognizer(
    supported_entity="PAN",
    patterns=[pan_pattern],
)

analyzer.registry.add_recognizer(
    aadhaar_recognizer
)
analyzer.registry.add_recognizer(
    pan_recognizer
)


def redact_pii(text: str):
    results = analyzer.analyze(
        text=text,
        language="en"
    )

    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=results
    )

    return anonymized.text, bool(results)