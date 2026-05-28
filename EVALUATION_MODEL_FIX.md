# Evaluation Model Fallback Issue - Fix Guide

## Problem
The evaluation service is always falling back to mock responses instead of using real LLM models for evaluation. This happens because the API calls to HuggingFace Router are failing.

## Root Causes Identified

### 1. **Invalid Model Names** ❌
**Original models in `evaluation_service.py`:**
```python
EVALUATION_MODELS = [
    "meta-llama/Llama-3.1-8B-Instruct:novita",    # ❌ Invalid :novita suffix
    "meta-llama/Llama-2-70b-chat-hf",
    "mistralai/Mistral-Large-Instruct-2407",
    "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
    "mistralai/Mistral-7B-Instruct-v0.2",
]
```

**Issue:** The `:novita` suffix is not a valid HuggingFace Router model name format. HuggingFace Router expects standard model identifiers in the format `org/model-name`.

**Status:** ✅ FIXED - Removed invalid model names

### 2. **Silent Fallback to Mock Mode** 🔄
When HuggingFace Router API calls fail (for any reason):
- The service catches exceptions and logs warnings
- It silently falls back to `generate_mock_response()` 
- Mock responses always succeed, so failures are hidden
- Users never know the real LLM wasn't used

**Location in code:**
- `huggingface_service.py` lines 116-152: Exception handling returns mock data
- `evaluation_service.py` lines 168-183: Model failover continues until all fail
- `evaluation_service.py` line 185: When all models fail, RuntimeError is raised (but it's caught by app error handler)

### 3. **No Visibility into Actual Failures** 👁️
The print statements at line 137-139 only show raw output:
```python
print("\n===== EVALUATION RAW OUTPUT =====\n")
print(generated_text)
print("\n==========================================\n")
```

But they don't show:
- Which model was used
- Whether it was a real response or mock
- Actual API error details

## How Fallback Currently Works

```
Request to evaluate answers
    ↓
Try Model 1 (Llama-3.1-8B) → API Fails (invalid name)
    ↓
Try Model 2 (Llama-2-70b) → API Fails or Timeout
    ↓
Try Model 3 (Mistral-7B) → API Fails or Timeout
    ↓
All models failed → RuntimeError raised → Caught by app
    ↓
⚠️ User sees generic error, never gets real evaluation
```

## Solutions Applied

### Solution 1: Fix Invalid Model Names ✅
**Changed models in `evaluation_service.py` (line 20-26):**
```python
EVALUATION_MODELS = [
    "meta-llama/Llama-3.1-8B-Instruct",      # ✅ Valid
    "mistralai/Mistral-7B-Instruct-v0.2",   # ✅ Valid
    "meta-llama/Llama-2-70b-chat-hf",       # ✅ Valid
]
```

These are the **correct HuggingFace Router compatible** model names.

### Solution 2: Add DEBUG Mode Setting ✅
**Added to `settings.py` (line 14):**
```python
DEBUG: bool = True
```

**Usage:**
- When `DEBUG=True`: Mock responses are used (development/testing)
- When `DEBUG=False`: Only real LLM responses are accepted (production)

Set in your `.env` file:
```env
DEBUG=False  # Production: Use real models only
DEBUG=True   # Development: Allow mock fallback
```

## Verification Steps

### 1. Check Current Setting
```bash
# Check .env file
cat backend/.env | grep DEBUG
```

### 2. Enable Real Models (Production)
```bash
# In backend/.env, set:
DEBUG=False
HUGGING_FACE_API_KEY=your_actual_key_here
```

### 3. Test Evaluation
```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload

# Test in another terminal
curl -X POST http://localhost:8000/api/learning/submit-round-1 \
  -H "Content-Type: application/json" \
  -d '{
    "student_name": "Test User",
    "topic": "Python",
    "questions": [
      {
        "question": "What is Python?",
        "correct_answer": "A programming language",
        "student_answer": "A programming language",
        "options": ["A snake", "A programming language", "A sport"]
      }
    ]
  }'
```

### 4. Check Logs
Look for these log messages:
- ✅ `[EVAL] Trying meta-llama/Llama-3.1-8B-Instruct` - Model is being attempted
- ✅ `[EVAL] Success using meta-llama/Llama-3.1-8B-Instruct` - Real model succeeded
- ❌ `[EVAL MODEL FAILED]` - Real model failed (API issue)
- ⚠️ `"source": "mock"` in response - Using mock fallback

## Why This Was Happening

1. **Invalid model names** were copied from third-party provider format
2. **HuggingFace Router** uses different naming conventions
3. **No error visibility** made it hard to diagnose
4. **Graceful fallback to mock** hid the failures

## How to Monitor Going Forward

### In Development
Keep `DEBUG=True` to allow mock fallback, but:
```python
# Monitor logs for these patterns:
if "source" in response:
    if response["source"] == "mock":
        log.warning("Using MOCK response - API issue detected")
```

### In Production
Set `DEBUG=False` and handle errors:
```python
# All API failures will raise exceptions
# Catch and notify users appropriately
try:
    evaluation = await evaluate_learning(request)
except RuntimeError as e:
    return {"error": "Evaluation service unavailable", "retry": True}
```

## Additional Notes

### HuggingFace Router Model Requirements
- Models must be accessible via HuggingFace Model Hub
- Must support Chat Completions API format
- Requires valid `HUGGING_FACE_API_KEY`

### Testing with Mock Mode
For development, mock responses are fine:
- They're contextually aware (based on score, topic)
- They follow the expected JSON format
- Perfect for UI/UX testing

Just remember to test with real models before production.

### API Timeout Issues
If you're getting timeouts:
- Increase timeout in `huggingface_service.py` line 83: `total=120` (2 minutes)
- Check HuggingFace API status
- Verify network connectivity to `router.huggingface.co`

## Checklist for Production

- [ ] Set `DEBUG=False` in `.env`
- [ ] Verify `HUGGING_FACE_API_KEY` is valid and has quota
- [ ] Test evaluation endpoint with real data
- [ ] Check logs for `[EVAL] Success` messages
- [ ] Monitor for `[EVAL MODEL FAILED]` patterns
- [ ] Set up alerts for evaluation failures
- [ ] Document fallback behavior for users
