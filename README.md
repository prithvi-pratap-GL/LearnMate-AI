# LearnMate-AI

AI-powered adaptive learning and assessment platform built using **FastAPI**, **React**, and **HuggingFace Router LLMs**.

LearnMate generates topic-specific quizzes, evaluates learner performance, and provides AI-assisted learning feedback while maintaining resilience against unreliable LLM outputs.

---

# Table of Contents

- Overview
- Features
- Architecture
- System Flow
- AI Pipelines
- Tech Stack
- Project Structure
- Installation
- Environment Variables
- Running the Project
- Swagger / API Docs
- API Endpoints
- Validation & Reliability Layer
- Mock Fallback & Toast Notifications
- Current Limitations
- Roadmap
- Contributing
- License

---

# Overview

LearnMate-AI is an educational platform designed to:

- Generate AI-powered MCQ quizzes
- Evaluate learner performance
- Provide learning feedback
- Support multi-round assessments
- Handle malformed LLM responses
- Transparently communicate fallback behavior

The system combines:

- LLM-generated content
- Deterministic evaluation
- Validation & repair layers
- Multi-model routing
- Frontend UX feedback

---

# Features

## AI Question Generation

Generate:

- Topic-specific questions
- Difficulty-aware MCQs
- Beginner / Intermediate / Advanced quizzes

Example:

```text
Topic: Python
Difficulty: Beginner
```

Returns:

- 5 validated MCQs
- 4 options each
- Correct answers

---

## Multi-Round Learning Flow

### Round 1

Core concept assessment.

Flow:

```text
Round 1
↓
Evaluation
↓
Pass?
↓
Round 2 unlocked
```

---

### Round 2

Advanced challenge assessment.

Focus:

- deeper understanding
- application
- concept mastery

---

## AI Evaluation

Evaluates:

- learner answers
- performance
- score
- feedback
- progression

---

## Multi-Model Failover

Evaluation supports multiple models.

Flow:

```text
Preferred Model
↓
Failure
↓
Try Next Model
↓
Success / Final Failure
```

This improves:

- availability
- reliability
- provider resilience

---

# Architecture

## High-Level Architecture

```text
Frontend (React + Vite)
        ↓
FastAPI Backend
        ↓
API Routes
        ↓
Services Layer
        ↓
HF Router LLM Models
        ↓
Validation + Repair
        ↓
Structured Response
```

---

## Backend Architecture

```text
app/
│
├── routes/
│       learning.py
│
├── services/
│       huggingface_service.py
│       question_service.py
│       evaluation_service.py
│
├── models/
│       schemas.py
│
├── utils/
│       prompts.py
│
├── config/
│       settings.py
│
└── main.py
```

---

## Frontend Architecture

```text
frontend/
│
├── pages/
│       QuizPage.tsx
│
├── components/
│
├── services/
│
├── App.tsx
│
└── main.tsx
```

---

# System Flow

## Question Generation Flow

```text
User Topic
↓
Frontend Request
↓
FastAPI Route
↓
Question Service
↓
Prompt Construction
↓
HF Router
↓
LLM Response
↓
JSON Extraction
↓
Repair
↓
Validation
↓
Frontend Response
```

---

## Evaluation Flow

```text
Submit Answers
↓
Evaluation Service
↓
Model Failover
↓
LLM Evaluation
↓
Parse
↓
Score + Feedback
↓
Frontend Result
```

---

# AI Pipelines

## Question Generation Pipeline

LearnMate uses a hardened AI pipeline.

Flow:

```text
Prompt
↓
HF Router
↓
raw_decode()
↓
json_repair()
↓
Pydantic Validation
↓
Business Validation
↓
Correction Retry
↓
Validated Questions
```

---

## Reliability Layer

The project does not trust LLM output blindly.

Protection layers:

### 1. JSON Extraction

Uses:

```python
JSONDecoder.raw_decode()
```

Prevents:

- partial parsing
- malformed output crashes

---

### 2. JSON Repair

Uses:

```python
json_repair
```

Repairs:

- broken brackets
- invalid quotes
- malformed JSON

---

### 3. Pydantic Validation

Schema:

```python
MCQQuestion
```

Checks:

- question present
- exactly 4 options
- answer consistency
- field validity

---

### 4. Business Validation

Ensures:

- no duplicate options
- usable question quality
- valid answers

---

### 5. Correction Retry

If validation fails:

```text
LLM
↓
Invalid JSON
↓
Correction Prompt
↓
Regeneration
```

This improves robustness.

---

# Tech Stack

## Frontend

- React
- TypeScript
- Vite
- Axios
- react-hot-toast

---

## Backend

- FastAPI
- Python
- Uvicorn
- aiohttp
- Pydantic
- json-repair

---

## AI Layer

- HuggingFace Router
- Llama
- Mistral
- Multi-model failover

---

# Installation

## Clone Repository

```bash
git clone <repo-url>
cd LearnMate-AI
```

---

# Backend Setup

Create virtual environment:

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

---

# Frontend Setup

Move:

```bash
cd frontend
```

Install:

```bash
npm install
```

---

# Environment Variables

Create:

```text
backend/.env
```

Example:

```env
HF_API_KEY=your_huggingface_token
DEBUG=True
```

Variables:

| Variable | Description |
|---|---|
| HF_API_KEY | HuggingFace Router token |
| DEBUG | Enables mock fallback |

---

# Running the Project

## Backend

From:

```text
backend/
```

Run:

```bash
python start.py
```

Expected:

```text
Uvicorn running on:
http://127.0.0.1:8000
```

---

## Frontend

From:

```text
frontend/
```

Run:

```bash
npm run dev
```

Default:

```text
http://localhost:5173
```

---

# Swagger / API Docs

FastAPI provides Swagger.

Open:

```text
http://localhost:8000/docs
```

Use Swagger to:

- test APIs
- inspect payloads
- debug backend

---

# API Endpoints

## Generate Questions

POST

```text
/api/learning/generate-questions
```

---

## Submit Round 1

POST

```text
/api/learning/submit-round-1
```

---

## Generate Round 2

POST

```text
/api/learning/generate-round-2-questions
```

---

## Submit Round 2

POST

```text
/api/learning/submit-round-2
```

---

## Analyze Learning

POST

```text
/api/learning/analyze-learning
```

---

# Mock Fallback & Toast UX

LearnMate avoids silent failures.

Flow:

```text
HF Failure
↓
Mock Fallback
↓
Backend source flag
↓
Frontend Toast
```

User sees:

```text
⚠ AI unavailable.
Showing demo questions.
```

This preserves:

- transparency
- trust
- usability

---

# Current Limitations

Current MVP limitations:

- evaluation still improving
- no persistence/database
- limited adaptive learning
- no authentication
- no user history

---

# Roadmap

Planned improvements:

## LLM-as-Judge

Semantic evaluation.

---

## Adaptive Difficulty

Difficulty adjusts dynamically.

---

## Learning Memory

Track weak concepts.

---

## Analytics Dashboard

Performance visualization.

---

## User Accounts

Authentication and progress tracking.

---

## Caching

Reduce LLM latency and cost.

---

# Contributing

Contributions welcome.

Steps:

1. Fork repository
2. Create branch

```bash
git checkout -b feature-name
```

3. Commit

```bash
git commit -m "feature"
```

4. Push

```bash
git push origin feature-name
```

5. Create Pull Request

---

# License

MIT License.

Use, modify, and distribute responsibly.

---

# Final Architecture Snapshot

```text
Frontend
↓
FastAPI
↓
Routes
↓
Services
↓
HF Router
↓
LLM
↓
raw_decode
↓
json_repair
↓
Pydantic
↓
Business Validation
↓
Correction Retry
↓
Frontend + Toast UX
```

LearnMate-AI combines AI generation with validation and recovery layers to create a more reliable educational learning experience.