# Quick Start - Run LearnMate AI with Timer, Ask AI & Database

## 🚀 30-Second Setup

### 1. Create Database (pgAdmin4)
- Open pgAdmin4 (http://localhost:5050)
- Right-click Databases → Create → Database
- Name: `learnmate`, Owner: `postgres`, Click Save

### 2. Update .env
Edit `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/learnmate
HUGGING_FACE_API_KEY=your_key_here
```

### 3. Start Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
✅ Tables created automatically, Backend at http://localhost:8000

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend at http://localhost:5173

---

## ✨ What You Can Now Do

### 🕐 Timer
- Quiz automatically shows dual timer in top-right
- Per-question timer: 0:00-5:00+ (MM:SS)
- Total session timer: 0:00-30:00+ (HH:MM:SS)
- Enable/Pause/Reset buttons
- Data saved to PostgreSQL

### 🤖 Ask AI
- Click "Ask AI" button on any question
- Choose "Hint" or "Full Explanation"
- Get AI-generated response
- Question marked "with help" badge
- Full points awarded
- Data saved to database

### 💾 Database
- Open pgAdmin4 → learnmate → query_tool
- Query timing data:
  ```sql
  SELECT * FROM question_timings WHERE session_id = 1;
  ```

---

## 📊 Verify It's Working

### Test Timer
1. Start quiz
2. Notice timer in top-right corner
3. Solve first question (~30 seconds)
4. Click Next → timer resets
5. Check DB:
   ```sql
   SELECT time_spent_seconds FROM question_timings LIMIT 1;
   ```

### Test Ask AI
1. On any question, click "Ask AI"
2. Select "Hint"
3. Click "Get Hint"
4. Read response
5. Check DB:
   ```sql
   SELECT ai_help_type FROM question_timings WHERE ai_help_used = true;
   ```

### Test Database
```sql
-- View all sessions
SELECT * FROM sessions;

-- View question timings
SELECT session_id, question_index, time_spent_seconds, ai_help_type 
FROM question_timings;

-- Average time per question
SELECT AVG(time_spent_seconds) as avg_time 
FROM question_timings;
```

---

## 🔧 If Something Breaks

### "Cannot connect to database"
- Check PostgreSQL is running: `pg_isready`
- Verify "learnmate" database exists
- Check `DATABASE_URL` in `.env`

### "Ask AI button doesn't work"
- Check `HUGGING_FACE_API_KEY` in `.env`
- Check backend is running on 8000
- Check browser console for errors

### "No tables in database"
- Restart backend (tables auto-create)
- Check `backend/app/models/database.py` exists
- Check `backend/app/main.py` has `Base.metadata.create_all()`

### "Frontend build fails"
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📝 File Locations

**Key Files:**
- Backend routes: `backend/app/routes/learning.py`
- Database models: `backend/app/models/database.py`
- Timer component: `frontend/src/components/QuizTimer.tsx`
- Ask AI component: `frontend/src/components/AskAI.tsx`
- Quiz page: `frontend/src/pages/QuizPage.tsx`

**Documentation:**
- Full setup guide: `DATABASE_SETUP.md`
- Implementation details: `IMPLEMENTATION_SUMMARY.md`
- Prompt improvements: `PROMPT_ROBUSTNESS_IMPROVEMENTS.md`

---

## 🎯 Next Steps

1. Complete a full quiz (both rounds)
2. Check database for all saved data
3. Experiment with Timer pause/reset
4. Try both Hint and Explanation modes
5. Query database to see patterns

---

## 💪 You're All Set!

Everything is installed, configured, and ready to use.

**Questions?** Check the documentation files or review the implementation summary.

**Have fun learning!** 🚀
