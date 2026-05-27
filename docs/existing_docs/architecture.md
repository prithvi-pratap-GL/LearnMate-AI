# LearnMate AI Architecture

## High-Level System Architecture

The application follows a modern client-server architecture with a React single-page application (SPA) for the frontend and a Python FastAPI async server for the backend, orchestrating a multi-round adaptive learning workflow.

```
┌──────────────────────────────────────────────────────────────────┐
│                   React Frontend (localhost:3000)                │
│                                                                  │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐│
│  │   QuizPage      │  │ ResultsDashboard │  │ Answer Review   ││
│  │  - Round 1      │  │  - Evaluation    │  │   Components    ││
│  │  - Round 2      │  │  - Solutions     │  │                 ││
│  │  - State Mgmt   │  │  - Roadmap       │  │                 ││
│  └─────────────────┘  └──────────────────┘  └─────────────────┘│
└────────────┬─────────────────────────────────────────────────────┘
             │ REST API (Axios)
             │ /api/learning/*
             │
┌────────────▼─────────────────────────────────────────────────────┐
│           FastAPI Backend (localhost:8000)                       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Routes Layer (/api/learning/)                              ││
│  │  ├─ POST /generate-questions (Round 1)                      ││
│  │  ├─ POST /submit-round-1 (Evaluate + Conditional)           ││
│  │  ├─ POST /generate-round-2-questions (Round 2)              ││
│  │  └─ POST /submit-round-2 (Evaluate + Solutions)             ││
│  └──────────────────┬──────────────────────────────────────────┘│
│                     │                                            │
│  ┌──────────────────▼──────────────────────────────────────────┐│
│  │  Services Layer (Business Logic)                            ││
│  │  ├─ question_service.py (Questions Rounds 1 & 2)            ││
│  │  ├─ evaluation_service.py (Scoring & Analysis)              ││
│  │  ├─ challenge_service.py (Solutions & Content)              ││
│  │  └─ roadmap_service.py (Learning Paths)                     ││
│  └──────────────────┬──────────────────────────────────────────┘│
│                     │                                            │
│  ┌──────────────────▼──────────────────────────────────────────┐│
│  │  Data Validation Layer (Pydantic)                           ││
│  │  ├─ QuestionAnswer (Question + Student Answer + Options)    ││
│  │  ├─ Round1SubmissionRequest                                 ││
│  │  └─ Round2SubmissionRequest                                 ││
│  └──────────────────┬──────────────────────────────────────────┘│
└────────────────────┼────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│    Hugging Face Inference API (Cloud LLM Service)              │
│    Model: mistralai/Mistral-7B-Instruct-v0.2                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture

### Technology Stack
- **Framework**: React 18+ with TypeScript
- **HTTP Client**: Axios for REST API calls
- **Styling**: Tailwind CSS (utility-first CSS framework)
- **Build Tool**: Create React App / Vite
- **Port**: `localhost:3000`

### Component Structure

```
App.tsx (Root)
  │
  └─── QuizPage.tsx (Main Container)
       │
       ├─── Input Section
       │    ├─ Student Name Input
       │    └─ Topic Input
       │
       ├─── Round 1 Quiz Section
       │    └─ Question Components
       │        ├─ Question Display
       │        ├─ Multiple Choice Options (Radio Buttons)
       │        └─ Student Answer Input (Textarea if no options)
       │
       ├─── Round 2 Quiz Section (Conditional)
       │    └─ Question Components (Advanced Difficulty)
       │
       └─── ResultsDashboard.tsx (Results Display)
            │
            ├─── Disqualification Message (If Round 1 < 50%)
            │
            ├─── Answer Review Sections
            │    ├─ Round 1 Review (5 Questions)
            │    │  ├─ Question Display
            │    │  ├─ Options Display
            │    │  ├─ Correct Answer
            │    │  ├─ Student Answer
            │    │  └─ Correctness Badge
            │    │
            │    └─ Round 2 Review (5 Questions) [If Round 2 completed]
            │       └─ Same as Round 1 Review
            │
            ├─── Evaluation Results Section
            │    ├─ Score Display
            │    ├─ Learning Level
            │    ├─ Strengths List
            │    └─ Weak Areas List
            │
            ├─── Generated Content Section (Solution/Explanation)
            │    └─ Topic-Specific Answer Explanations
            │
            └─── Roadmap Section
                 └─ 30-Day Personalized Learning Plan
```

### State Management (QuizPage.tsx)

```typescript
const [studentName, setStudentName] = useState('');              // User input
const [topic, setTopic] = useState('');                         // User input
const [currentRound, setCurrentRound] = useState(0);            // 0=Input, 1=R1, 2=R2
const [questions, setQuestions] = useState<IQuestion[]>([]);    // Current round questions
const [round1Questions, setRound1Questions] = useState([]);     // Preserved R1 questions
const [round1Evaluation, setRound1Evaluation] = useState(null); // R1 evaluation
const [round1Score, setRound1Score] = useState(null);          // R1 score
const [result, setResult] = useState<IAnalysisResult | null>(); // Final results
const [loading, setLoading] = useState(false);                 // Loading state
const [error, setError] = useState<string | null>(null);       // Error messages
```

### Data Flow

```
User Input
  ↓
Generate Round 1 Questions (API Call)
  ↓
Display Questions (State: currentRound=1)
  ↓
User Answers Questions
  ↓
Submit Round 1 (API Call)
  ├─ Backend: Evaluate answers (Score calculation)
  ├─ IF Score < 50%:
  │  ├─ Generate beginner explanation
  │  ├─ Generate roadmap
  │  └─ Display results (State: result, currentRound=0)
  └─ IF Score ≥ 50%:
     ├─ Store Round 1 data (State: round1Questions, round1Evaluation, round1Score)
     ├─ Generate Round 2 questions
     └─ Display Round 2 (State: currentRound=2)
        ↓
        User Answers Round 2 Questions
        ↓
        Submit Round 2 (API Call)
        ├─ Backend: Evaluate Round 2 answers
        ├─ Generate solution explanations
        ├─ Generate advanced roadmap
        └─ Display comprehensive results with both reviews
```

---

## Backend Architecture

### Technology Stack
- **Framework**: FastAPI 0.104+
- **Server**: Uvicorn ASGI server
- **Validation**: Pydantic v2
- **Async**: Python async/await
- **Port**: `localhost:8000`
- **LLM API**: Hugging Face Inference API

### Directory Structure

```
backend/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py
│   │   ├─ FastAPI app initialization
│   │   ├─ CORS middleware configuration
│   │   ├─ Router registration (/api/learning)
│   │   └─ Global error handler middleware
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── learning.py (Main routes file)
│   │       ├─ POST /generate-questions (Round 1)
│   │       ├─ POST /submit-round-1
│   │       ├─ POST /generate-round-2-questions
│   │       └─ POST /submit-round-2
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── huggingface_service.py (LLM API wrapper)
│   │   │   └─ query_model(prompt) → LLM response
│   │   ├── question_service.py
│   │   │   ├─ generate_questions(topic, difficulty) → Questions
│   │   │   └─ Mock data for development
│   │   ├── evaluation_service.py
│   │   │   └─ evaluate_learning(request) → Evaluation result
│   │   ├── challenge_service.py
│   │   │   ├─ generate_solution_explanation(topic, questions) → Solutions
│   │   │   └─ generate_advanced_challenges(topic, strengths) → Advanced content
│   │   └── roadmap_service.py
│   │       └─ generate_roadmap(level, strengths, weak_areas) → Learning plan
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py (Pydantic models)
│   │       ├─ QuestionAnswer
│   │       │  ├─ question: str
│   │       │  ├─ correct_answer: str
│   │       │  ├─ student_answer: str
│   │       │  └─ options: List[str] = []
│   │       ├─ Round1SubmissionRequest
│   │       ├─ Round2SubmissionRequest
│   │       └─ LearningAnalysisRequest
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── prompts.py (Centralized LLM prompts)
│   │       ├─ QUESTION_GENERATION_PROMPT
│   │       ├─ EVALUATION_PROMPT
│   │       ├─ SOLUTION_EXPLANATION_PROMPT ← NEW for Round 2
│   │       ├─ ADVANCED_CHALLENGES_PROMPT
│   │       └─ ROADMAP_PROMPT
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── error_handler.py
│   │       └─ Global exception handling
│   │
│   └── config/
│       ├── __init__.py
│       └── settings.py
│           └─ Application configuration & env vars
│
├── tests/
│   └─ Unit and integration tests
│
├── start.py (Server entry point)
├── requirements.txt
├── .env (Environment variables - NOT in git)
└── .gitignore
```

### API Routes with Router Prefix

All routes are registered with prefix `/api/learning`:

```python
# backend/app/main.py
app.include_router(router, prefix="/api/learning")

# Results in endpoints:
# POST /api/learning/generate-questions
# POST /api/learning/submit-round-1
# POST /api/learning/generate-round-2-questions
# POST /api/learning/submit-round-2
```

### Pydantic Schema Models

```python
class QuestionAnswer(BaseModel):
    """Single question with student's answer"""
    question: str
    correct_answer: str
    student_answer: str
    options: List[str] = []  # Multiple choice options
    model_config = ConfigDict(str_strip_whitespace=True)

class Round1SubmissionRequest(BaseModel):
    """Round 1 submission payload"""
    student_name: str
    topic: str
    questions: List[QuestionAnswer]

class Round2SubmissionRequest(BaseModel):
    """Round 2 submission payload"""
    student_name: str
    topic: str
    questions: List[QuestionAnswer]
    round_1_score: int
    round_1_evaluation: dict

class LearningAnalysisRequest(BaseModel):
    """Legacy request model"""
    student_name: str
    topic: str
    questions: List[QuestionAnswer]
```

---

## Complete LLM Workflow

### Two-Round Adaptive Flow

```
User Starts Assessment
  │
  ├─ ROUND 1: BEGINNER ASSESSMENT
  │  │
  │  └─ LLM CALL 0: Generate Round 1 Questions
  │     Prompt: QUESTION_GENERATION_PROMPT (Beginner difficulty)
  │     Output: 5 beginner-level questions with multiple-choice options
  │     Service: question_service.generate_questions(topic="Python", difficulty="beginner")
  │
  ├─ User Answers Round 1 Questions
  │  │
  │  └─ LLM CALL 1: Evaluate Round 1 Answers
  │     Prompt: EVALUATION_PROMPT
  │     Input: Topic + Student answers + Correct answers
  │     Output: {score, strengths, weak_areas, level}
  │     Service: evaluation_service.evaluate_learning(request)
  │
  ├─ Score Evaluation Check
  │  │
  │  ├─ IF Score < 50%: DISQUALIFIED PATH
  │  │  │
  │  │  ├─ LLM CALL 2A: Generate Beginner Explanation
  │  │  │  Prompt: BEGINNER_EXPLANATION_PROMPT
  │  │  │  Output: Simple explanation + examples + exercises
  │  │  │  Service: challenge_service.generate_beginner_explanation()
  │  │  │
  │  │  ├─ LLM CALL 3: Generate Roadmap
  │  │  │  Prompt: ROADMAP_PROMPT
  │  │  │  Output: 30-day beginner learning path
  │  │  │  Service: roadmap_service.generate_roadmap(level="Beginner", ...)
  │  │  │
  │  │  └─ Display Results:
  │  │     - Disqualification message
  │  │     - Answer Review (Round 1)
  │  │     - Beginner Learning Explanation
  │  │     - Beginner Roadmap
  │  │     - END ASSESSMENT
  │  │
  │  └─ ELSE (Score ≥ 50%): ROUND 2 PATH ✓
  │     │
  │     ├─ ROUND 2: ADVANCED ASSESSMENT
  │     │  │
  │     │  └─ LLM CALL 2B: Generate Round 2 Advanced Questions
  │     │     Prompt: QUESTION_GENERATION_PROMPT (Advanced difficulty)
  │     │     Output: 5 advanced-level questions
  │     │     Service: question_service.generate_questions(topic, difficulty="advanced")
  │     │
  │     ├─ User Answers Round 2 Questions
  │     │  │
  │     │  └─ LLM CALL 1 (AGAIN): Evaluate Round 2 Answers
  │     │     Prompt: EVALUATION_PROMPT
  │     │     Input: Advanced questions + Student answers
  │     │     Output: {score, strengths, weak_areas, level}
  │     │     Service: evaluation_service.evaluate_learning(request)
  │     │
  │     ├─ LLM CALL 2C: Generate Solution Explanations (NEW)
  │     │  Prompt: SOLUTION_EXPLANATION_PROMPT
  │     │  Input: Topic + Round 2 questions + Score
  │     │  Output: Answer-wise explanations (why each answer is correct)
  │     │  Service: challenge_service.generate_solution_explanation(topic, questions, score)
  │     │
  │     ├─ LLM CALL 3 (AGAIN): Generate Advanced Roadmap
  │     │  Prompt: ROADMAP_PROMPT
  │     │  Input: Advanced level + Strengths + Weak areas
  │     │  Output: 30-day advanced learning path with expert-level goals
  │     │  Service: roadmap_service.generate_roadmap(level="Advanced", ...)
  │     │
  │     └─ Display Results:
  │        - Success message (both R1 & R2 scores)
  │        - Round 1 Answer Review (5 questions)
  │        - Round 2 Answer Review (5 advanced questions)
  │        - Solution Explanations (Why each answer is right)
  │        - Advanced Evaluation Results
  │        - Advanced Learning Roadmap
  │        - END ASSESSMENT

Total LLM Calls:
  • Round 1 only: 3 calls (Questions, Evaluation, Roadmap)
  • Round 1 + Round 2: 5 calls (↑ + Advanced Questions, Evaluation, Solutions, Roadmap)
```

---

## Data Flow Diagrams

### Round 1 → Disqualified (Score < 50%)

```
┌─────────────────┐
│  User Input     │
│  Name + Topic   │
└────────┬────────┘
         │ POST /api/learning/generate-questions
         ↓
    ┌────────────────┐
    │  Backend       │
    │  Query LLM 0   │
    │  (Questions)   │
    └────────┬───────┘
             │ Response: 5 questions with options
             ↓
    ┌────────────────────┐
    │  Frontend          │
    │  Display R1 Quiz   │
    │  (5 Questions)     │
    └────────┬───────────┘
             │ User answers all questions
             │ POST /api/learning/submit-round-1
             ↓
    ┌──────────────────────┐
    │  Backend             │
    │  1. Query LLM 1      │
    │     (Evaluation)     │
    │  2. Calculate Score  │
    │  3. Check: Score<50% │
    │  4. Query LLM 2A     │
    │     (Beginner Expl.) │
    │  5. Query LLM 3      │
    │     (Roadmap)        │
    └────────┬─────────────┘
             │ Response: Evaluation + Content + Roadmap
             ↓
    ┌────────────────────────────┐
    │  Frontend                  │
    │  Display Results:          │
    │  - Disqualified Message    │
    │  - Answer Review (R1)      │
    │  - Beginner Explanation    │
    │  - Learning Roadmap        │
    └────────────────────────────┘
```

### Round 1 → Pass → Round 2 (Score ≥ 50%)

```
┌─────────────────┐
│  User Input     │
│  Name + Topic   │
└────────┬────────┘
         │ POST /api/learning/generate-questions
         ↓
    ┌────────────────┐
    │  Backend       │
    │  Query LLM 0   │
    │  (Questions)   │
    └────────┬───────┘
             │ Response: 5 questions with options
             ↓
    ┌────────────────────┐
    │  Frontend          │
    │  Display R1 Quiz   │
    │  (5 Questions)     │
    └────────┬───────────┘
             │ User answers all questions
             │ POST /api/learning/submit-round-1
             ↓
    ┌──────────────────────────┐
    │  Backend                 │
    │  1. Query LLM 1          │
    │     (Evaluation)         │
    │  2. Calculate Score      │
    │  3. Check: Score >= 50%  │
    │     ✓ QUALIFIED!         │
    │  4. Store R1 data        │
    └────────┬─────────────────┘
             │ Response: Qualification message
             ↓
    ┌────────────────────────────┐
    │  Frontend                  │
    │  Display Transition Msg    │
    │  "Generating Round 2..."   │
    └────────┬───────────────────┘
             │ POST /api/learning/generate-round-2-questions
             ↓
    ┌────────────────────────┐
    │  Backend               │
    │  Query LLM 2B          │
    │  (Advanced Questions)  │
    └────────┬───────────────┘
             │ Response: 5 advanced questions with options
             ↓
    ┌────────────────────┐
    │  Frontend          │
    │  Display R2 Quiz   │
    │  (5 Questions)     │
    │  (Advanced Level)  │
    └────────┬───────────┘
             │ User answers all questions
             │ POST /api/learning/submit-round-2
             ↓
    ┌───────────────────────────────┐
    │  Backend                      │
    │  1. Query LLM 1 (again)       │
    │     (R2 Evaluation)           │
    │  2. Calculate Score           │
    │  3. Query LLM 2C              │
    │     (Solution Explanations)   │
    │  4. Query LLM 3 (again)       │
    │     (Advanced Roadmap)        │
    └────────┬──────────────────────┘
             │ Response: Full results + solutions
             ↓
    ┌───────────────────────────────────┐
    │  Frontend                         │
    │  Display Comprehensive Results:   │
    │  - Success Message (R1 + R2)      │
    │  - Answer Review (Round 1)        │
    │  - Answer Review (Round 2)        │
    │  - Solution Explanations          │
    │  - Evaluation Results             │
    │  - Advanced Learning Roadmap      │
    └───────────────────────────────────┘
```

---

## Service Layer Details

### Question Service
```python
async def generate_questions(topic: str, difficulty: str = "beginner")
  → Uses QUESTION_GENERATION_PROMPT
  → Difficulty levels: "beginner" (Round 1), "advanced" (Round 2)
  → Returns: List[{question, correct_answer, options}]
  → LLM Call: Hugging Face API
```

### Evaluation Service
```python
async def evaluate_learning(request: LearningAnalysisRequest)
  → Uses EVALUATION_PROMPT
  → Analyzes student answers vs. correct answers
  → Returns: {score, strengths, weak_areas, level}
  → LLM Call: Hugging Face API
  → Used in: Round 1 and Round 2
```

### Challenge Service
```python
async def generate_solution_explanation(topic: str, questions: list, score: int)
  → Uses SOLUTION_EXPLANATION_PROMPT
  → NEW function for Round 2 answer explanations
  → Returns: {type: "solution", content: "detailed_explanations"}
  → LLM Call: Hugging Face API
  → Used in: Round 2 /submit-round-2 endpoint

async def generate_advanced_challenges(topic: str, strengths: list)
  → Uses ADVANCED_CHALLENGES_PROMPT
  → Returns: {type: "advanced_challenges", content: "..."}
  → Used in: Round 1 when score ≥ 50% (now skipped in favor of Round 2)
```

### Roadmap Service
```python
async def generate_roadmap(level: str, strengths: list, weak_areas: list)
  → Uses ROADMAP_PROMPT
  → Generates 30-day personalized learning plan
  → Returns: {title: "...", content: "..."}
  → LLM Call: Hugging Face API
  → Used in: Both Round 1 (disqualified) and Round 2 (final)
```

---

## Error Handling Strategy

```
┌─────────────────────┐
│  API Request        │
└──────────┬──────────┘
           │
           ↓
    ┌─────────────────────────────────┐
    │  Input Validation               │
    │  (Pydantic schemas)             │
    └──────────────┬────────────────┬─┘
                   │                │
              ✓ Valid          ✗ Invalid
                   │                │
                   ↓                ↓
            ┌───────────────┐  ┌──────────────┐
            │  Process      │  │  422 Error   │
            │  Request      │  │ (Validation) │
            └───────┬───────┘  └──────────────┘
                    │
                    ↓
        ┌─────────────────────────────┐
        │  LLM API Call               │
        │  (with timeout: 20s)        │
        └──────────┬──────────────────┘
                   │
         ┌─────────┴────────────┐
         │                      │
      ✓ Success            ✗ Failure
         │                      │
         ↓                      ↓
    ┌──────────────┐    ┌──────────────────────┐
    │  Parse       │    │  Handle Error:       │
    │  Response    │    │  - Timeout           │
    │  → JSON      │    │  - Network Error     │
    └──────┬───────┘    │  - API Error         │
           │            └──────────┬───────────┘
           │                       │
           ↓                       ↓
    ┌──────────────┐    ┌──────────────────────┐
    │  Return      │    │  500 Error Response  │
    │  Success     │    │  User-Friendly Msg   │
    │  Response    │    └──────────────────────┘
    └──────────────┘
```

---

## Deployment Considerations

### Backend Requirements
- Python 3.8+
- FastAPI 0.104+
- Uvicorn
- Pydantic v2
- Python-multipart
- Requests library

### Frontend Requirements
- Node.js 16+
- React 18+
- TypeScript 4.9+
- Axios
- Tailwind CSS

### Environment Variables
```
HUGGING_FACE_API_KEY=your_api_key
```

### CORS Configuration
Currently configured for local development:
```
Frontend: http://localhost:3000
Backend: http://localhost:8000
```

For production, update CORS allowed origins in `main.py`.

---

## Performance & Optimization

### Async Operations
- All backend operations are async for concurrent request handling
- Non-blocking I/O for API calls to Hugging Face

### Timeout Handling
- 20-second timeout for LLM API calls
- Automatic error handling if timeout exceeded

### Frontend Optimizations
- React state caching for answers
- Conditional rendering to minimize re-renders
- Lazy loading of components

---

## Testing Strategy

See [test-cases.md](test-cases.md) for comprehensive test scenarios covering:
- Frontend validation
- API endpoint testing
- AI workflow verification
- Error handling scenarios
- End-to-end assessment flow (both Round 1 and Round 2)
