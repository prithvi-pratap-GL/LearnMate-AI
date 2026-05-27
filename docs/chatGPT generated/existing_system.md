# LearnMate AI - Existing System Documentation

## Overview

LearnMate AI is an AI-powered adaptive learning and assessment platform.

The system allows users to:

- Enter their name and topic
- Receive AI-generated MCQ questions
- Submit answers
- Receive evaluation and performance analysis
- Get personalized learning recommendations and roadmap

The platform follows a **two-round adaptive assessment model**.

---

# Purpose

The purpose of LearnMate AI is to:

- Assess topic understanding
- Dynamically adapt difficulty
- Identify weak concepts
- Provide AI-assisted learning feedback
- Generate personalized study guidance

The project acts as an intelligent learning assistant rather than a static quiz system.

---

# Tech Stack

## Frontend

- React
- TypeScript
- Vite
- TailwindCSS
- Axios
- React Router

## Backend

- FastAPI
- Python
- Pydantic
- aiohttp

## AI Layer

- Hugging Face Inference API

---

# High-Level Architecture

```text
Frontend
    ↓
API Routes
    ↓
Service Layer
    ↓
HuggingFace AI API
    ↓
Evaluation + Roadmap Logic
    ↓
Frontend Response
```

The system uses a layered architecture:

- Presentation Layer → Frontend UI
- Routing Layer → API endpoints
- Service Layer → Business logic
- AI Layer → LLM interactions

---

# Backend Architecture

## Main Entry

Primary backend:

```text
backend/app/main.py
```

Responsibilities:

- FastAPI initialization
- Middleware setup
- CORS configuration
- Route registration
- Health endpoints

---

## Backend Startup Files

Multiple startup files exist:

```text
start.py
run_server.py
minimal_server.py
```

This creates multiple possible execution paths.

---

## Routes Layer

### `routes/learning.py`

Handles:

- Question generation
- Answer submission
- Evaluation
- Learning analysis
- Roadmap generation

Base route:

```text
/api/learning
```

---

## Service Layer

Business logic is organized into services.

---

### `question_service.py`

Responsibilities:

- Generate MCQs
- Build prompts
- Parse LLM responses
- Structure questions

---

### `evaluation_service.py`

Responsibilities:

- Evaluate answers
- Calculate score
- Generate explanations
- Produce performance feedback

---

### `roadmap_service.py`

Responsibilities:

- Learning analysis
- Weakness identification
- Personalized roadmap creation

---

### `challenge_service.py`

Responsibilities:

- Round 2 adaptive difficulty
- Follow-up challenge generation

---

# Configuration Layer

Configuration handled in:

```text
config/settings.py
```

Uses:

- Pydantic Settings

Responsibilities:

- Load environment variables
- Manage configuration values

---

# Prompt Layer

Prompt engineering stored in:

```text
utils/prompts.py
```

Contains:

- Question prompts
- Evaluation prompts
- Learning analysis prompts
- Recommendation prompts

This centralizes LLM behavior.

---

# Frontend Architecture

Main workflow handled through:

## QuizPage

Responsibilities:

- User input
- API communication
- Question display
- Answer handling
- Assessment progression

---

## ResultsDashboard

Responsibilities:

- Score rendering
- Evaluation feedback
- Learning roadmap display
- Recommendations

---

## API Communication

Uses:

- Axios

---

## Routing

Uses:

- React Router

---

# System Workflow

## Step 1

User enters:

- Name
- Topic

Frontend requests:

```http
POST /generate-questions
```

---

## Step 2

Backend:

- Builds prompt
- Calls Hugging Face API
- Generates Round 1 MCQs

---

## Step 3

User submits Round 1.

Request:

```http
POST /submit-round-1
```

Backend:

- Evaluates responses
- Calculates score
- Generates feedback

---

## Step 4

Adaptive branching.

### Score < 50

System:

- Identifies weak areas
- Generates roadmap
- Ends assessment

### Score ≥ 50

System:

- Generates Round 2
- Increases challenge difficulty

---

## Step 5

Round 2 generation.

Request:

```http
POST /generate-round-2-questions
```

---

## Step 6

Final submission.

Request:

```http
POST /submit-round-2
```

System returns:

- Final score
- Explanations
- Learning feedback
- Personalized roadmap

---

# API Endpoints

## Learning APIs

### Generate Questions

```http
POST /api/learning/generate-questions
```

---

### Submit Round 1

```http
POST /api/learning/submit-round-1
```

---

### Generate Round 2

```http
POST /api/learning/generate-round-2-questions
```

---

### Submit Round 2

```http
POST /api/learning/submit-round-2
```

---

### Analyze Learning

```http
POST /api/learning/analyze-learning
```

---

### Health Endpoint

```http
GET /
```

---

# Environment Variables

Expected:

```env
HUGGING_FACE_API_KEY=
```

Loaded through:

```text
backend/app/config/settings.py
```

---

# Running the Project

## Backend

Install:

```bash
cd backend
pip install -r requirements.txt
```

Run:

```bash
python start.py
```

Default:

```text
localhost:8000
```

---

## Frontend

Install:

```bash
cd frontend
npm install
```

Run:

```bash
npm run dev
```

Default:

```text
localhost:5173
```

---

# Folder Structure

Simplified:

```text
backend/
│
├── app/
│   ├── routes/
│   ├── services/
│   ├── config/
│   └── utils/

frontend/
│
└── src/
    ├── pages/
    ├── components/
    └── services/
```

---

# Current Limitations

Current system limitations:

- No authentication
- No database
- No user persistence
- No Docker setup
- No CI/CD
- Heavy LLM dependency
- Fragile JSON parsing
- Hardcoded URLs in frontend
- Multiple backend startup paths

---

# Summary

LearnMate AI is an adaptive AI-based assessment and learning assistant built using FastAPI, React, and Hugging Face.

Its architecture is modular and service-oriented, but still early-stage and requires production hardening and system improvements.