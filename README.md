# LearnMate AI - Two-Round Adaptive Learning Assessment Platform

An intelligent two-round adaptive learning assessment system that dynamically evaluates student understanding, provides answer-wise feedback, and generates personalized learning roadmaps.

## Features

- **Two-Round Adaptive Assessment**:
  - Round 1: 5 beginner-level questions with multiple-choice options
  - Round 2: 5 advanced-level questions (for students scoring ≥50% in Round 1)
  
- **Answer Review Sections**:
  - Question-by-question comparison of student answers vs. correct answers
  - Visual indicators (green/red) for correct/incorrect responses
  - Display of all available options with correct answer highlighted
  
- **Solution Explanations**:
  - Topic-specific explanations of why each answer is correct
  - Technical reasoning and key takeaways
  - Common misconceptions to avoid
  
- **Adaptive Progression**:
  - Students scoring <50% in Round 1 receive beginner-level learning paths
  - Students scoring ≥50% proceed to advanced Round 2
  
- **Personalized Roadmaps**:
  - LLM-generated learning paths based on assessment level
  - 30-day structured learning plans with milestones
  - Tailored to strengths and weak areas identified in evaluation

- **Dynamic Question Generation**:
  - Unique questions generated per session using Hugging Face API
  - Different difficulty levels (beginner for Round 1, advanced for Round 2)
  - Multiple-choice options automatically generated for each question

## Tech Stack

**Backend:**
- FastAPI with Uvicorn
- Python 3.8+
- Pydantic for data validation
- Async/await for concurrent request handling
- Hugging Face Inference API for LLM calls

**Frontend:**
- React with TypeScript
- Axios for HTTP requests
- Tailwind CSS for styling
- Responsive design for all screen sizes

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app initialization
│   │   ├── routes/
│   │   │   └── learning.py            # Two-round quiz endpoints
│   │   ├── services/
│   │   │   ├── question_service.py    # Question generation (Round 1 & 2)
│   │   │   ├── evaluation_service.py  # Answer evaluation
│   │   │   ├── challenge_service.py   # Solution explanations (Round 2)
│   │   │   └── roadmap_service.py     # Personalized learning paths
│   │   ├── models/
│   │   │   └── schemas.py             # Pydantic models
│   │   └── utils/
│   │       └── prompts.py             # LLM prompts
│   ├── start.py                       # Server entry point
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   └── QuizPage.tsx           # Two-round quiz workflow
    │   ├── components/
    │   │   └── ResultsDashboard.tsx   # Results with answer review & solutions
    │   └── App.tsx
    ├── package.json
    └── tsconfig.json
```

## Setup & Running

### Backend

```bash
cd backend
pip install -r requirements.txt
python start.py
```

Server runs on `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

## API Endpoints

All endpoints use the `/api/learning/` prefix.

### Round 1 Endpoints

```
POST /api/learning/generate-questions
```
Generate 5 beginner-level questions for Round 1.

**Request:**
```json
{
  "topic": "Python Programming"
}
```

**Response:**
```json
{
  "questions": [
    {
      "question": "What is the fundamental principle behind Python?",
      "correct_answer": "Python emphasizes readability and simplicity...",
      "options": ["Option A", "Option B", "Option C", "Option D"]
    }
  ],
  "round": 1,
  "total_questions": 5
}
```

---

```
POST /api/learning/submit-round-1
```
Submit Round 1 answers and get evaluation.

**Request:**
```json
{
  "student_name": "John",
  "topic": "Python Programming",
  "questions": [
    {
      "question": "What is Python?",
      "correct_answer": "A programming language",
      "student_answer": "A programming language",
      "options": ["...", "...", "..."]
    }
  ]
}
```

**Response (Score < 50% - Does not qualify for Round 2):**
```json
{
  "status": "Round 1 Complete",
  "round": 1,
  "score": 40,
  "evaluation": {
    "score": 40,
    "strengths": ["..."],
    "weak_areas": ["..."],
    "level": "Beginner"
  },
  "generated_content": {
    "type": "performance_analysis",
    "content": "Detailed feedback on performance..."
  },
  "roadmap": {
    "title": "Personalized Roadmap for Beginner",
    "content": "30-day learning plan..."
  },
  "questions": [...],
  "can_proceed_to_round_2": false
}
```

**Response (Score ≥ 50% - Qualifies for Round 2):**
```json
{
  "status": "Round 1 Complete - Proceeding to Round 2",
  "round": 1,
  "score": 75,
  "can_proceed_to_round_2": true,
  "evaluation": {
    "score": 75,
    "strengths": ["..."],
    "weak_areas": ["..."],
    "level": "Intermediate"
  },
  "generated_content": {...},
  "roadmap": {...},
  "questions": [...]
}
```

### Round 2 Endpoints (Conditional)

```
POST /api/learning/generate-round-2-questions
```
Generate 5 advanced-level questions for Round 2 (only if Round 1 score ≥ 50%).

**Request:**
```json
{
  "topic": "Python Programming"
}
```

**Response:**
```json
{
  "questions": [
    {
      "question": "How would you optimize a Python application for performance?",
      "correct_answer": "Using profiling, caching, and async patterns...",
      "options": ["Option A", "Option B", "Option C", "Option D"]
    }
  ],
  "round": 2,
  "total_questions": 5
}
```

---

```
POST /api/learning/submit-round-2
```
Submit Round 2 answers and get comprehensive analysis with solution explanations.

**Request:**
```json
{
  "student_name": "John",
  "topic": "Python Programming",
  "questions": [...],
  "round_1_score": 75,
  "round_1_evaluation": {...}
}
```

**Response:**
```json
{
  "status": "Assessment Complete",
  "round": 2,
  "round_1_score": 75,
  "round_2_evaluation": {
    "score": 82,
    "strengths": ["Advanced problem-solving", "..."],
    "weak_areas": ["Performance optimization", "..."],
    "level": "Advanced"
  },
  "generated_content": {
    "type": "solution",
    "content": "Question 1: Why this answer is correct...\nQuestion 2: Technical explanation..."
  },
  "roadmap": {
    "title": "Personalized Roadmap for Advanced",
    "content": "Expert-level 30-day learning plan..."
  },
  "questions": [...]
}
```

## How It Works

### Complete Two-Round Flow

```
1. Student enters name and topic
   ↓
2. System generates 5 beginner questions (Round 1)
   ↓
3. Student answers questions
   ↓
4. System evaluates answers (LLM CALL 1)
   ↓
5. Check Score:
   
   IF Score < 50%:
   ├─ Generate beginner explanation (LLM CALL 2A)
   ├─ Generate personalized roadmap (LLM CALL 3)
   └─ Display: Disqualified message + Answer Review + Learning Path
   
   ELSE (Score ≥ 50%):
   ├─ Generate Round 2 advanced questions (LLM CALL 2B)
   ├─ Student answers 5 advanced questions
   ├─ Evaluate Round 2 answers (LLM CALL 1 again)
   ├─ Generate solution explanations (LLM CALL 2C)
   ├─ Generate advanced roadmap (LLM CALL 3)
   └─ Display: Round 1 Review + Round 2 Review + Solutions + Advanced Path
```

### Results Display

For **Round 1 Failures** (< 50%):
- ❌ Disqualification message
- 📋 Answer Review (5 questions with feedback)
- 📊 Evaluation Results (score, strengths, weak areas)
- 📝 Beginner Learning Path
- 🗺️ Personalized Roadmap

For **Round 2 Completions** (≥ 50%):
- ✅ Success message with both scores
- 📋 Round 1 Answer Review (5 beginner questions)
- 📋 Round 2 Answer Review (5 advanced questions)
- 💡 Solution Section (answer-wise explanations)
- 🎯 Advanced Evaluation Results
- 🗺️ Advanced Personalized Roadmap

## Answer Review Format

Each question in the answer review section displays:

```
┌─────────────────────────────────────────────┐
│ Question 1                                  │
├─────────────────────────────────────────────┤
│ Question: [Full question text]              │
│                                             │
│ Options:                                    │
│ • Option A                                  │
│ • Option B (Correct Answer) ✓               │
│ • Option C                                  │
│ • Option D                                  │
│                                             │
│ ✓ Correct Answer: Option B                  │
│ ✓ Your Answer: Option B                     │
│                                             │
│ [CORRECT ✓]                                 │
└─────────────────────────────────────────────┘
```

## Solution Explanations (Round 2)

The Solution section provides detailed, topic-specific explanations:

```
## Question 1: [Question text]
**Correct Answer:** [Answer]

**Why This is Correct:**
- Explanation of why this answer is right
- Technical reasoning and key concepts
- Connection to the topic

**Key Takeaway:**
- Important point to remember
- Common misconceptions to avoid
```

## Error Handling

The system gracefully handles various error scenarios:

- **Empty fields**: Validation errors for required inputs
- **API failures**: User-friendly error messages
- **Timeouts**: Automatic timeout handling for LLM calls
- **Invalid responses**: JSON parsing error recovery

## Environment Variables

Create a `.env` file in the backend directory:

```
HUGGING_FACE_API_KEY=your_api_key_here
```

**Note:** The `.env` file is added to `.gitignore` and should never be committed to version control.

## Testing the Application

### Test Scenario 1: Failed Round 1
1. Start backend and frontend
2. Enter: Name = "Alice", Topic = "Advanced Machine Learning"
3. Try to answer questions poorly (wrong/brief answers)
4. Expected: Score < 50% → Disqualified message + Beginner Learning Path

### Test Scenario 2: Passed Round 1 & Complete Round 2
1. Start backend and frontend
2. Enter: Name = "Bob", Topic = "JavaScript Basics"
3. Answer Round 1 questions well (good/detailed answers)
4. Expected: Score ≥ 50% → Proceed to Round 2 automatically
5. Answer Round 2 advanced questions
6. Expected: Complete results with both reviews and solution explanations

### Test Scenario 3: Different Topics
- Try different topics: "Python", "Web Development", "Data Science", "Cloud Computing"
- Each topic should generate unique questions and topic-specific explanations

## Browser Compatibility

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Considerations

- **Timeout**: LLM calls timeout after 20 seconds
- **Async Operations**: All backend operations are asynchronous for better performance
- **Frontend Caching**: Answers are cached in React state during assessment

## Security

- API key is kept on the backend only (never exposed to frontend)
- CORS is configured for local development (localhost:3000 ↔ localhost:8000)
- Input validation on both frontend and backend
- No sensitive data is logged

For more security details, see [security-review.md](security-review.md)

## Future Enhancements

- Add user authentication and history tracking
- Implement progress analytics dashboard
- Add more question types (matching, fill-in-the-blank)
- Support for multiple languages
- Offline mode support
- Real-time progress notifications

## License

MIT

## Support

For issues or questions:
- Check [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md) for recent updates
- Review [architecture.md](architecture.md) for technical details
- See [test-cases.md](test-cases.md) for test scenarios
