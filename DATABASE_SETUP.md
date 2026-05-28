# Database Setup Guide - LearnMate AI

## Overview
LearnMate AI now uses PostgreSQL to store quiz sessions, question timings, and AI help usage data. Follow these steps to set up the database.

## Prerequisites
- PostgreSQL installed and running
- pgAdmin4 installed (for database management)
- Python 3.9+ with virtual environment activated
- Backend dependencies installed: `pip install -r backend/requirements.txt`

## Step 1: Create Database in PostgreSQL

### Option 1: Using pgAdmin4 (GUI)
1. Open pgAdmin4 in your browser (usually http://localhost:5050)
2. Right-click on "Databases" → "Create" → "Database"
3. Name: `learnmate`
4. Owner: `postgres`
5. Click "Save"

### Option 2: Using psql (Command Line)
```bash
psql -U postgres
CREATE DATABASE learnmate;
\q
```

## Step 2: Update .env File

Create or update `backend/.env` with:

```env
HUGGING_FACE_API_KEY=your_api_key_here

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/learnmate
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=learnmate

# Safety and Debug
DEBUG=True
ENABLE_PII=True
ENABLE_TOXICITY=True
ENABLE_INJECTION=True
ENABLE_POLICY=True
TOXICITY_THRESHOLD=0.6
INJECTION_THRESHOLD=0.7
```

**Note:** If you set a custom password for PostgreSQL during installation, update `DB_PASSWORD` and `DATABASE_URL` accordingly.

## Step 3: Initialize Database Tables

The database tables are automatically created when you start the backend server. The ORM models defined in `backend/app/models/database.py` will be created automatically via SQLAlchemy.

## Step 4: Verify Setup

### Check Database Connection
```bash
cd backend
python -m uvicorn app.main:app --reload
```

You should see:
- No database connection errors
- Backend running on http://localhost:8000

### Verify Tables in pgAdmin4
1. Open pgAdmin4
2. Navigate to: Databases → learnmate → Schemas → public → Tables
3. You should see:
   - `users` table
   - `sessions` table
   - `question_timings` table

## How It Works

### Tables Overview

**users**
- Stores student names and creation timestamp
- Each student gets a unique user_id

**sessions**
- Stores quiz session information
- Fields: session_uuid, user_id, topic, round, status, started_at, completed_at
- One session per quiz attempt (Round 1 or Round 2)

**question_timings**
- Stores per-question timing data and AI help usage
- Fields: session_id, question_index, question_text, time_spent_seconds, ai_help_used, ai_help_type, student_answer, correct_answer, is_correct, created_at

### Data Flow

1. **Quiz Start**
   - User enters name and topic
   - Frontend calls `/api/learning/create-session`
   - Backend creates Session record, returns session_uuid
   - Frontend stores session_uuid in state

2. **During Quiz**
   - User answers questions and can use "Ask AI" feature
   - When navigating to next question, frontend calls `/api/learning/save-question-timing`
   - Backend saves QuestionTiming record with:
     - Time spent on that question
     - Student answer & correct answer
     - AI help type if used ("hint" or "explanation")

3. **Quiz End**
   - User submits final answers
   - Frontend calls `/api/learning/complete-session`
   - Backend marks Session as "completed"

## Features Enabled

### 🕐 Timer
- Per-question timer (resets for each question)
- Total session timer (cumulative)
- Enable/disable and reset buttons
- Data saved to database

### 🤖 Ask AI
- Choose between Hint or Full Explanation
- Marks question as "with help"
- Stores help type in database
- Generates AI response using HuggingFace API

### 📊 Analytics (Future)
The data structure enables:
- Track time spent per question
- Identify which students used AI help
- Analyze learning patterns
- Compare performance with/without AI help

## Troubleshooting

### Connection Error: "Unable to connect to database"
- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in `.env` is correct
- Verify database "learnmate" exists in pgAdmin4

### Tables Not Created
- Restart backend server (tables auto-create on startup)
- Check backend logs for SQLAlchemy errors
- Manually run: `python -c "from app.models.database import Base; from app.db.database import engine; Base.metadata.create_all(bind=engine)"`

### Timeout on /ask-ai Endpoint
- Ensure HUGGING_FACE_API_KEY is set in `.env`
- Check HuggingFace API is accessible
- In DEBUG=True mode, mock data is used for fallback

## Database Reset (Development Only)

To completely reset the database:

```bash
# Drop and recreate database
psql -U postgres -c "DROP DATABASE learnmate;"
psql -U postgres -c "CREATE DATABASE learnmate;"

# Tables will be auto-created on next backend start
```

## Production Notes

For production deployment:
- Use strong, unique `DB_PASSWORD`
- Move DATABASE_URL to environment variables (not .env)
- Enable SSL for PostgreSQL connections
- Set `DEBUG=False`
- Use connection pooling for multiple backend instances
- Regular database backups recommended

## Monitoring Queries

### View all sessions
```sql
SELECT * FROM sessions;
```

### View question timings for a session
```sql
SELECT * FROM question_timings WHERE session_id = 1;
```

### Count AI help usage
```sql
SELECT ai_help_type, COUNT(*) FROM question_timings 
WHERE ai_help_used = true 
GROUP BY ai_help_type;
```

### Average time per question
```sql
SELECT question_index, AVG(time_spent_seconds) 
FROM question_timings 
GROUP BY question_index;
```
