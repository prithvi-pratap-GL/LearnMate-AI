# Testing Guide for Backend Fixes

## Quick Start

### 1. Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

Backend will be available at: `http://localhost:8000`

### 2. Start Frontend (in another terminal)
```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## End-to-End Testing

### Test Case 1: Round 1 Complete (≥50% to unlock Round 2)

**Steps:**
1. Go to `http://localhost:5173`
2. Click "Start Assessment"
3. Enter name: "Test User"
4. Enter topic: "Python"
5. Click "Generate Round 1 Questions"
6. **Expected:** 5 questions appear with proper formatting
   - Each question text is complete
   - Each question has exactly 4 options (full text, no letters/brackets)
   - Options are clickable cards (not radio buttons)
7. Answer all 5 questions (try to get them all correct)
8. Click "Submit Answers"
9. **Expected Results Page:**
   - Circular score ring showing 100% (if all correct) or 80%, 60%, etc.
   - Status shows "Round 1 + Round 2" badge at top
   - Can proceed to Round 2 (button appears)

**What's Fixed Here:**
- ✅ Questions generated with correct JSON format (no corrupted options)
- ✅ Score calculation is percentage-based (100% for all correct, not 50%)

### Test Case 2: Round 1 Failed (<50%, no Round 2)

**Steps:**
1. Go through Round 1 setup as before
2. Intentionally answer questions incorrectly or leave some unanswered
3. Submit and get below 50%
4. **Expected Results Page:**
   - Shows score below 50% in red-ish tones
   - Shows "Performance Analysis" 
   - NO Round 2 button
   - Shows personalized roadmap based on weak areas

**What's Fixed Here:**
- ✅ Score correctly reflects answers (3/5 = 60%, not 50%)

### Test Case 3: Round 2 Complete (Proceed after Round 1)

**Steps:**
1. Complete Round 1 with ≥50% score
2. Button/prompt to "Proceed to Round 2" appears
3. Click to proceed
4. **Expected:** 5 advanced questions appear
   - Should NOT be duplicates of Round 1 questions
   - Questions are "advanced" level (more complex)
5. Answer all Round 2 questions
6. Click "Submit Answers"
7. **Expected Results Dashboard:**
   - TWO score rings visible:
     - Left ring: Round 1 score (e.g., 80%)
     - Right ring: Round 2 score (e.g., 70%)
   - "Score Comparison" card shows both scores in bar charts
   - Header shows "Round 1 + Round 2" badge
   - Answer Review tab shows ALL 10 answers (5 from each round)

**What's Fixed Here:**
- ✅ Round 1 data preserved and shown in Round 2 results
- ✅ Both evaluations displayed properly
- ✅ Score ring animations work correctly

### Test Case 4: Check Answer Review

**Steps:**
1. Complete both rounds
2. Click "Answer Review" tab in results
3. **Expected for Round 2 Results:**
   - Shows all 10 questions (5 from Round 1 + 5 from Round 2)
   - Each question shows:
     - Question number
     - "✓ Correct" or "✗ Incorrect" badge
   - Click to expand and see:
     - Options as colored pills (green = correct, red = wrong, gray = not selected)
     - Your answer highlighted
     - Explanation of why it's correct/wrong

**What's Fixed Here:**
- ✅ All answers from both rounds shown
- ✅ Judge responses are complete (no missing fields)

### Test Case 5: Check AI Analysis

**Steps:**
1. Complete both rounds
2. Click "AI Analysis" tab
3. **Expected:**
   - Content is properly formatted (no raw JSON dumps)
   - Has section headers (##, ###)
   - Has bullet points with arrows
   - Looks like readable analysis

**What's Fixed Here:**
- ✅ Evaluation prompt returns complete JSON
- ✅ Content parsing works correctly

### Test Case 6: Check Learning Roadmap

**Steps:**
1. Complete both rounds
2. Click "Learning Roadmap" tab
3. **Expected:**
   - Structured roadmap with milestones
   - Shows numbered steps if available
   - Properly formatted with visual hierarchy
   - Not just raw text dump

## Debug Verification

### Check Backend Logs

While running the backend, look for these log messages:

✅ **Good Signs:**
```
[EVAL] Trying meta-llama/Llama-3.1-8B-Instruct
[EVAL] Success using meta-llama/Llama-3.1-8B-Instruct
===== RAW MODEL OUTPUT =====
[{...valid JSON...}]
```

❌ **Problem Signs:**
```
[JSON REPAIR] Attempting repair...
[EVAL PARSE FAILED] 
[EVAL MODEL FAILED]
[JUDGE FAILED]
```

### Check Frontend Network Requests

Open DevTools (F12) → Network tab and look for:

1. **POST `/api/learning/generate-questions`**
   - Response should have `questions` array with 5 items
   - Each question should have: `question`, `options` (4 items), `correct_answer`

2. **POST `/api/learning/submit-round-1`**
   - Response should have: `score` (0-100), `evaluation` object with `strengths`, `weak_areas`, `level`

3. **POST `/api/learning/generate-round-2-questions`**
   - Check request body includes `round_1_questions`
   - Response should have 5 different advanced questions

4. **POST `/api/learning/submit-round-2`**
   - Response should have `round_2_evaluation` with complete score data
   - Also includes `round_1_score` from request

## Common Issues & Solutions

### Issue: "All evaluation models failed"
**Cause:** HuggingFace API not responding or invalid API key
**Solution:** Check `HUGGING_FACE_API_KEY` in `.env`

### Issue: Questions have corrupted options like `["A"]`
**Cause:** Prompt still not specific enough for this LLM model
**Solution:** Log shows which model is being used, may need to adjust prompt further

### Issue: Judge returning incomplete responses
**Cause:** LLM judge not following the 3-field structure
**Solution:** Check logs for `[JUDGE FAILED]` - may indicate API issues

### Issue: Round 1 score is always 50%
**Cause:** Score calculation not fixed (old version running)
**Solution:** Make sure backend code has the percentage calculation fix

### Issue: Round 2 doesn't show Round 1 data
**Cause:** Frontend not preserving Round 1 evaluation
**Solution:** Check that `setRound1Evaluation()` is being called in QuizPage

## Performance Expectations

- Round 1 Question Generation: ~3-5 seconds
- Round 1 Evaluation: ~2-3 seconds  
- Round 2 Question Generation: ~4-6 seconds (might retry if too many duplicates)
- Round 2 Evaluation: ~2-3 seconds

If significantly slower, check HuggingFace API status.

## Success Criteria

All of the following should be true for fixes to be working:

- [ ] 5 Round 1 questions generate with proper JSON format
- [ ] Options are complete text strings (no letters/brackets/prefixes)
- [ ] Score calculation is 0-100% based on correct answers
- [ ] 100% score appears when all answers are correct
- [ ] Round 2 proceeds if Round 1 ≥ 50%
- [ ] Round 2 questions don't duplicate Round 1
- [ ] Results show both Round 1 and Round 2 scores with rings
- [ ] Answer Review shows all 10 answers (both rounds)
- [ ] AI Analysis is properly formatted
- [ ] Learning Roadmap is structured, not raw text
- [ ] No JSON repair errors in logs
- [ ] Judge returns complete evaluation objects
