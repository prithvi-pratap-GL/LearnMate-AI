# Issue Resolution Log: LLM Integration & Question Generation Stabilization

## Overview

Resolved multiple issues related to LLM integration, model routing, JSON parsing, and AI-generated question validation in the LearnMate-AI backend.

---

## Problems Identified

### 1. HuggingFace Router Integration Failure
**Issue:**  
LLM requests returned `404 Not Found`.

**Root Cause:**  
The project used HuggingFace Router Chat Completions endpoint with an incompatible inference payload and malformed URL construction.

**Fix:**  
- Preserved original request-based pipeline
- Updated `query_model()` to use:
  - HF Router Chat Completions API
  - correct payload structure
  - proper model routing

---

### 2. Mock Response Fallback Masking Errors
**Issue:**  
Application silently returned mock questions while real API requests failed.

**Root Cause:**  
Broad exception handling triggered `generate_mock_response()` for all failures.

**Fix:**  
- Added debugging visibility
- Improved logging
- Identified real API failures instead of hidden fallback behavior

---

### 3. Unsupported Evaluation Models
**Issue:**  
Round-1 evaluation failed with `400 model_not_supported`.

**Root Cause:**  
Hardcoded evaluation models were unsupported by enabled HF providers.

**Fix:**  
Implemented **multi-model failover**:

```text
Preferred model
↓
Failure
↓
Automatically try next model
```

This preserved original architecture while improving resilience.

---

### 4. Fragile LLM JSON Parsing
**Issue:**  
AI responses frequently caused:

- JSONDecodeError
- malformed arrays
- duplicated keys
- broken quotes
- nested JSON

**Root Cause:**  
Parser relied on naive `find()` / `rfind()` extraction and assumed valid JSON.

**Fix:**  
Implemented:

- `JSONDecoder.raw_decode()`
- `json_repair`
- safer extraction logic

---

### 5. Missing Schema Validation
**Issue:**  
Invalid MCQ structures passed parsing but contained unusable content.

Examples:
- missing fields
- invalid options
- incorrect answer mismatch

**Fix:**  
Added **Pydantic validation** using `MCQQuestion`.

Validated:

- question quality
- exactly 4 options
- unique options
- answer-option consistency

---

### 6. LLM Output Reliability Issues
**Issue:**  
Open models occasionally returned malformed or incomplete JSON.

**Fix:**  
Implemented **correction retry pipeline**.

Flow:

```text
LLM
↓
Parse
↓
Repair
↓
Validate
↓
Retry with correction prompt
↓
Return validated questions
```

---

## Final Result

Question generation pipeline is now significantly more stable and fault tolerant.

Current architecture:

```text
HF Router
↓
query_model()
↓
raw_decode
↓
json_repair
↓
Pydantic validation
↓
Correction retry
↓
Validated MCQs
```

---

## Outcome

- Stable HF LLM integration
- Reduced parsing failures
- Improved question reliability
- Preserved original architecture
- Added resilience without replacing core pipeline