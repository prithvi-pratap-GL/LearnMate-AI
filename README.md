# LearnMate AI - Adaptive Learning Assessment Platform

An intelligent two-round learning assessment system that dynamically evaluates student understanding and provides personalized learning roadmaps.

## Features

- **Two-Round Assessment**: Beginner Round 1 (5 questions) and Advanced Round 2 (for qualified students)
- **Intelligent Evaluation**: Dynamic scoring based on answer quality and length analysis
- **Adaptive Progression**: Students scoring <50% on Round 1 receive beginner explanations; ≥50% proceed to Round 2
- **Personalized Roadmaps**: LLM-generated learning paths based on strengths and weak areas
- **Dynamic Content Generation**: Questions and options are different each session with topic-aware context
- **UTF-8 Safe**: Handles special characters and encoding issues on Windows

## Tech Stack

**Backend:**
- FastAPI with Uvicorn
- Python 3.8+
- Pydantic for data validation
- Async/await for concurrent request handling

**Frontend:**
- React with TypeScript
- Axios for HTTP requests
- Tailwind CSS for styling

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app initialization
│   │   ├── routes/
│   │   │   └── learning.py      # Quiz endpoints
│   │   ├── services/
│   │   │   ├── question_service.py
│   │   │   ├── evaluation_service.py
│   │   │   ├── challenge_service.py
│   │   │   └── roadmap_service.py
│   │   └── models/
│   │       └── schemas.py       # Pydantic models
│   ├── start.py                 # Server entry point
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   └── QuizPage.tsx      # Main quiz workflow
    │   ├── components/
    │   │   └── ResultsDashboard.tsx
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

- `POST /api/generate-questions` - Generate Round 1 questions
- `POST /api/submit-round-1` - Submit and evaluate Round 1
- `POST /api/generate-round-2-questions` - Generate Round 2 questions (if qualified)
- `POST /api/submit-round-2` - Submit and evaluate Round 2

## How It Works

1. Student enters name and topic
2. System generates 5 beginner-level questions with dynamic options
3. Student answers questions
4. System evaluates answers and calculates score
5. If score < 50%:
   - Display results with beginner explanation and roadmap
   - End assessment
6. If score ≥ 50%:
   - Generate advanced Round 2 questions
   - Student answers 5 advanced questions
   - Display comprehensive analysis and personalized roadmap

## License

MIT
