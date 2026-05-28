import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ResultsDashboard from '../components/ResultsDashboard';
import { AskAI } from '../components/AskAI';
import toast from 'react-hot-toast';
import type { IQuestion, IEvaluation, IAnalysisResult } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ApiQuestion {
  question: string;
  correct_answer: string;
  options?: string[];
}

const QuizPage: React.FC = () => {
  const [studentName, setStudentName] = useState('');
  const [topic, setTopic] = useState('');
  const [currentRound, setCurrentRound] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [questions, setQuestions] = useState<IQuestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [generatingQuestions, setGeneratingQuestions] = useState(false);
  const [result, setResult] = useState<IAnalysisResult | null>(null);
  const [round1Evaluation, setRound1Evaluation] = useState<IEvaluation | null>(null);
  const [round1Score, setRound1Score] = useState<number | null>(null);
  const [round1Questions, setRound1Questions] = useState<IQuestion[]>([]);
  const [sessionUuid, setSessionUuid] = useState<string>('');
  const [aiHelpByQuestion, setAiHelpByQuestion] = useState<Record<number, string>>({});
  const [questionSeconds, setQuestionSeconds] = useState(0);
  const [totalSeconds, setTotalSeconds] = useState(0);
  const [timerRunning, setTimerRunning] = useState(true);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Timer interval
  useEffect(() => {
    if (!timerRunning || currentRound === 0 || result) return;

    const interval = setInterval(() => {
      setTotalSeconds(prev => prev + 1);
      setQuestionSeconds(prev => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [timerRunning, currentRound, result]);

  // Starfield for setup screen
  useEffect(() => {
    if (currentRound !== 0 || result) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    if (!ctx) return;

    let W: number = canvas.width = window.innerWidth;
    let H: number = canvas.height = window.innerHeight;

    interface Star {
      x: number;
      y: number;
      r: number;
      o: number;
      tw: number;
      ts: number;
      spd: number;
    }

    let stars: Star[] = Array.from({ length: 160 }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.3 + 0.2,
      o: Math.random() * 0.6 + 0.1,
      tw: Math.random() * Math.PI * 2,
      ts: Math.random() * 0.015 + 0.004,
      spd: Math.random() * 0.08 + 0.01
    }));

    function draw() {
      ctx!.clearRect(0, 0, W, H);
      stars.forEach(s => {
        s.tw += s.ts;
        const op = s.o * (0.5 + 0.5 * Math.sin(s.tw));
        ctx!.beginPath();
        ctx!.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx!.fillStyle = `rgba(200, 210, 255, ${op})`;
        ctx!.fill();
        s.x -= s.spd;
        if (s.x < -2) { s.x = W + 2; s.y = Math.random() * H; }
      });
      requestAnimationFrame(draw);
    }

    function resize() {
      W = (canvas as HTMLCanvasElement).width = window.innerWidth;
      H = (canvas as HTMLCanvasElement).height = window.innerHeight;
    }

    window.addEventListener('resize', resize);
    draw();

    return () => window.removeEventListener('resize', resize);
  }, [currentRound, result]);

  const handleGenerateRound1Questions = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!studentName.trim() || !topic.trim()) {
      toast.error('Please enter both name and topic');
      return;
    }
    setGeneratingQuestions(true);

    try {
      // Create session first
      const sessionResponse = await axios.post(`${API_BASE}/api/learning/create-session`, {
        student_name: studentName,
        topic,
        round: 1
      });
      setSessionUuid(sessionResponse.data.session_uuid);

      const response = await axios.post(`${API_BASE}/api/learning/generate-questions`, { topic });
      const generatedQuestions = response.data.questions.map((q: ApiQuestion) => ({
        question: q.question,
        correct_answer: q.correct_answer,
        student_answer: '',
        options: q.options || []
      }));
      setQuestions(generatedQuestions);
      setCurrentRound(1);
      setCurrentQuestion(0);
      setAiHelpByQuestion({});
      setQuestionSeconds(0);
      setTotalSeconds(0);
      setTimerRunning(true);
    } catch (err) {
      toast.error('Failed to generate questions. Please try again.');
      console.error('Error generating questions', err);
    } finally {
      setGeneratingQuestions(false);
    }
  };

  const handleQuestionChange = (index: number, answer: string) => {
    const newQuestions = [...questions];
    newQuestions[index].student_answer = answer;
    setQuestions(newQuestions);
  };

  const saveQuestionTiming = async (questionIndex: number, timeSpent: number) => {
    if (!sessionUuid) return;

    try {
      const q = questions[questionIndex];
      await axios.post(`${API_BASE}/api/learning/save-question-timing`, {
        session_uuid: sessionUuid,
        question_index: questionIndex,
        question_text: q.question,
        time_spent_seconds: timeSpent,
        student_answer: q.student_answer,
        correct_answer: q.correct_answer,
        ai_help_type: aiHelpByQuestion[questionIndex] || null
      });
    } catch (err) {
      console.error('Error saving question timing:', err);
    }
  };

  const handleAIHelpUsed = (questionIndex: number, helpType: string) => {
    setAiHelpByQuestion(prev => ({
      ...prev,
      [questionIndex]: helpType
    }));
  };

  const handleSubmitRound1 = async (e: React.FormEvent) => {
    e.preventDefault();
    if (questions.some(q => !q.student_answer)) {
      toast.error('Please answer all questions');
      return;
    }
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/api/learning/submit-round-1`, {
        student_name: studentName,
        topic,
        questions
      });
      const data = response.data;

      if (data.can_proceed_to_round_2) {
        toast.success('Great! Moving to Round 2');
        setRound1Evaluation(data.evaluation);
        setRound1Score(data.score);
        setRound1Questions(questions);
        await generateRound2Questions();
      } else {
        setResult({
          status: data.status,
          round: 1,
          evaluation: data.evaluation,
          generated_content: data.generated_content,
          roadmap: data.roadmap,
          questions,
          can_proceed_to_round_2: false
        });
      }
    } catch (err) {
      toast.error('Round 1 submission failed.');
      console.error('Error submitting Round 1', err);
    } finally {
      setLoading(false);
    }
  };

  const generateRound2Questions = async () => {
    setGeneratingQuestions(true);
    try {
      const response = await axios.post(`${API_BASE}/api/learning/generate-round-2-questions`, {
        topic,
        round_1_questions: round1Questions
      });
      const generatedQuestions = response.data.questions.map((q: ApiQuestion) => ({
        question: q.question,
        correct_answer: q.correct_answer,
        student_answer: '',
        options: q.options || []
      }));
      setQuestions(generatedQuestions);
      setCurrentRound(2);
      setCurrentQuestion(0);
    } catch (err) {
      toast.error('Failed to generate Round 2 questions. Please try again.');
      console.error('Error generating Round 2 questions', err);
    } finally {
      setGeneratingQuestions(false);
    }
  };

  const handleSubmitRound2 = async (e: React.FormEvent) => {
    e.preventDefault();
    if (questions.some(q => !q.student_answer)) {
      toast.error('Please answer all questions');
      return;
    }
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/api/learning/submit-round-2`, {
        student_name: studentName,
        topic,
        questions,
        round_1_score: round1Score || 0,
        round_1_evaluation: round1Evaluation,
        round_1_questions: round1Questions
      });
      setResult({
        status: response.data.status,
        round: 2,
        round_1_score: round1Score || 0,
        round_1_evaluation: round1Evaluation || undefined,
        round_2_evaluation: response.data.round_2_evaluation,
        generated_content: response.data.generated_content,
        roadmap: response.data.roadmap,
        questions: response.data.questions || questions,
        can_proceed_to_round_2: true
      });
    } catch (err) {
      toast.error('Failed to submit Round 2. Please try again.');
      console.error('Error submitting Round 2', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    // Complete current session if it exists
    if (sessionUuid) {
      try {
        await axios.post(`${API_BASE}/api/learning/complete-session`, {
          session_uuid: sessionUuid,
          status: 'abandoned'
        });
      } catch (err) {
        console.error('Error completing session:', err);
      }
    }

    setStudentName('');
    setTopic('');
    setQuestions([]);
    setCurrentRound(0);
    setCurrentQuestion(0);
    setResult(null);
    setRound1Evaluation(null);
    setRound1Score(null);
    setRound1Questions([]);
    setSessionUuid('');
    setAiHelpByQuestion({});
    setQuestionSeconds(0);
    setTotalSeconds(0);
    setTimerRunning(false);
  };

  const handleNavigateQuestion = async (direction: number) => {
    const next = currentQuestion + direction;
    if (next >= 0 && next < questions.length) {
      // Save timing for current question before moving
      await saveQuestionTiming(currentQuestion, questionSeconds);

      setCurrentQuestion(next);
      setQuestionSeconds(0);
    }
  };

  const unansweredCount = questions.filter(q => !q.student_answer).length;
  const currentQ = questions[currentQuestion];

  // Setup screen
  if (currentRound === 0 && !result) {
    return (
      <div className="relative min-h-screen overflow-hidden">
        <canvas ref={canvasRef} className="fixed inset-0 z-0 pointer-events-none" />
        <div className="fixed inset-0 z-0 pointer-events-none">
          <div className="absolute w-96 h-96 rounded-full blur-3xl opacity-10" style={{ background: 'rgba(99, 102, 241, 0.3)', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }} />
        </div>

        <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md border-b border-[var(--border)] bg-[rgba(10,10,15,0.7)]">
          <div className="px-12 h-16 flex items-center">
            <a href="/" className="flex items-center gap-2 font-bold text-lg">
              <div className="w-8 h-8 bg-[var(--accent)] rounded flex items-center justify-center">
                <svg className="w-4 h-4 fill-white" viewBox="0 0 24 24"><path d="M13 2L4.09 12.26c-.36.44-.55.66-.55.88 0 .2.08.39.21.53.15.16.36.33.88.33H12l-1 8 8.91-10.26c.36-.44.55-.66.55-.88a.72.72 0 0 0-.21-.53c-.15-.16-.36-.33-.88-.33H13l1-8z"/></svg>
              </div>
              LearnMate AI
            </a>
          </div>
        </nav>

        <div className="relative z-10 min-h-screen flex items-center justify-center p-6 pt-32">
          <div className="w-full max-w-xl bg-[var(--surface)] border border-[var(--border2)] rounded-3xl p-12">
            <div className="text-xs font-bold text-[var(--accent2)] tracking-widest uppercase mb-4">New Assessment</div>
            <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: 'Syne' }}>Start your learning session</h1>
            <p className="text-[var(--text2)] mb-8 leading-relaxed">Enter your name and the topic you want to be assessed on. The AI will generate questions in seconds.</p>

            <form onSubmit={handleGenerateRound1Questions} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-[var(--text2)] mb-2">Your name</label>
                <div className="relative">
                  <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text3)]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  <input type="text" value={studentName} onChange={(e) => setStudentName(e.target.value)} placeholder="e.g. Riya Sharma" className="w-full px-4 py-3 pl-10 bg-[rgba(255,255,255,0.04)] border border-[var(--border2)] rounded-lg focus:border-[rgba(99,102,241,0.5)] focus:outline-none transition" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--text2)] mb-2">Topic to assess</label>
                <div className="relative mb-3">
                  <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text3)]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                  <input type="text" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="e.g. Python, Machine Learning, React…" className="w-full px-4 py-3 pl-10 bg-[rgba(255,255,255,0.04)] border border-[var(--border2)] rounded-lg focus:border-[rgba(99,102,241,0.5)] focus:outline-none transition" />
                </div>
                <div className="flex flex-wrap gap-2">
                  {['Python', 'Machine Learning', 'React', 'System Design', 'SQL', 'Docker'].map(chip => (
                    <button key={chip} type="button" onClick={() => setTopic(chip)} className="text-xs px-3 py-1.5 rounded-full bg-[rgba(255,255,255,0.05)] border border-[var(--border2)] text-[var(--text2)] hover:border-[rgba(99,102,241,0.4)] hover:text-[var(--accent2)] transition">
                      {chip}
                    </button>
                  ))}
                </div>
              </div>

              <div className="h-px bg-[var(--border)]"></div>

              <button type="submit" disabled={generatingQuestions || !studentName.trim() || !topic.trim()} className="w-full px-6 py-3 bg-[var(--accent)] text-white font-semibold rounded-lg hover:bg-[var(--accent2)] disabled:opacity-40 transition">
                Generate Round 1 Questions
              </button>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-[rgba(255,255,255,0.03)] border border-[var(--border)] rounded-lg p-4 text-center">
                  <div className="text-sm font-bold text-[var(--accent2)]" style={{ fontFamily: 'Syne' }}>Round 1 — Foundations</div>
                  <div className="text-xs text-[var(--text3)] mt-1">5 beginner questions</div>
                </div>
                <div className="bg-[rgba(255,255,255,0.03)] border border-[var(--border)] rounded-lg p-4 text-center">
                  <div className="text-sm font-bold text-purple-400" style={{ fontFamily: 'Syne' }}>Round 2 — Advanced</div>
                  <div className="text-xs text-[var(--text3)] mt-1">Score ≥50% to unlock</div>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // Quiz screen
  if ((currentRound === 1 || currentRound === 2) && !result && currentQ) {
    const roundLabel = currentRound === 1 ? 'Round 1 — Foundations' : 'Round 2 — Advanced';
    return (
      <div className="bg-[var(--bg)]">
        {/* Navbar */}
        <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md border-b border-[var(--border)] bg-[rgba(10,10,15,0.8)]">
          <div className="max-w-2xl mx-auto px-8 h-16 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2 font-bold">
              <div className="w-7 h-7 bg-[var(--accent)] rounded flex items-center justify-center">
                <svg className="w-3.5 h-3.5 fill-white" viewBox="0 0 24 24"><path d="M13 2L4.09 12.26c-.36.44-.55.66-.55.88 0 .2.08.39.21.53.15.16.36.33.88.33H12l-1 8 8.91-10.26c.36-.44.55-.66.55-.88a.72.72 0 0 0-.21-.53c-.15-.16-.36-.33-.88-.33H13l1-8z"/></svg>
              </div>
              LearnMate AI
            </a>
            <div className="flex items-center gap-6">
              <span className="text-xs px-3 py-1 rounded-full bg-[var(--accent-glow)] border border-[rgba(99,102,241,0.25)] text-[var(--accent2)]">{topic}</span>
              <span className="text-xs px-3 py-1 rounded-full bg-[rgba(255,255,255,0.05)] border border-[var(--border2)] text-[var(--text2)]">{roundLabel}</span>

              {/* Timer in navbar */}
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-2 px-3 py-1 bg-[rgba(99,102,241,0.1)] border border-[rgba(99,102,241,0.3)] rounded-lg">
                  <span className="text-xs font-mono text-[var(--accent2)] font-bold min-w-[50px]">
                    Q: {String(Math.floor(questionSeconds / 60)).padStart(2, '0')}:{String(questionSeconds % 60).padStart(2, '0')}
                  </span>
                  <span className="text-[var(--border2)]">|</span>
                  <span className="text-xs font-mono text-[var(--text2)] min-w-[50px]">
                    {String(Math.floor(totalSeconds / 3600)).padStart(2, '0')}:{String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0')}:{String(totalSeconds % 60).padStart(2, '0')}
                  </span>
                </div>

                <button
                  onClick={() => setTimerRunning(!timerRunning)}
                  className="p-1 text-[var(--text2)] hover:text-[var(--accent2)] transition"
                  title={timerRunning ? "Pause" : "Resume"}
                >
                  {timerRunning ? (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/></svg>
                  ) : (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                  )}
                </button>

                <button
                  onClick={() => setQuestionSeconds(0)}
                  disabled={!timerRunning}
                  className="p-1 text-[var(--text2)] hover:text-[var(--accent2)] disabled:opacity-50 disabled:cursor-not-allowed transition"
                  title="Reset question timer"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M1 4v6h6M23 20v-6h-6"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64M3.51 15A9 9 0 0 0 18.36 18.36"/></svg>
                </button>
              </div>

              <button onClick={handleReset} className="text-sm text-[var(--text3)] hover:text-[var(--text2)] transition">✕ Exit</button>
            </div>
          </div>
        </nav>

        <div className="max-w-2xl mx-auto px-6 py-24">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-[var(--text2)]">Question <strong className="text-[var(--text)]">{currentQuestion + 1}</strong> of {questions.length}</span>
              <span className="text-sm text-[var(--text2)]">{questions.filter(q => q.student_answer).length} answered</span>
            </div>
            <div className="flex gap-1">
              {questions.map((_, idx) => (
                <div key={idx} className={`flex-1 h-1 rounded-full ${idx < currentQuestion ? 'bg-[var(--accent)]' : idx === currentQuestion ? 'bg-[rgba(99,102,241,0.5)]' : 'bg-[rgba(255,255,255,0.08)]'}`}></div>
              ))}
            </div>
          </div>

          <div className="bg-[var(--surface)] border border-[var(--border2)] rounded-2xl p-10 mb-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-9 h-9 rounded-full bg-[var(--accent-glow)] border border-[rgba(99,102,241,0.25)] flex items-center justify-center text-sm font-bold text-[var(--accent2)]">{currentQuestion + 1}</div>
              <span className="text-xs font-bold tracking-widest uppercase text-[var(--text3)]">Multiple choice</span>
            </div>
            <p className="text-lg leading-relaxed mb-8">{currentQ.question}</p>

            <div className="space-y-2">
              {currentQ.options?.map((option, idx) => (
                <button key={idx} onClick={() => handleQuestionChange(currentQuestion, option)} className={`w-full flex items-center gap-4 p-4 rounded-2xl border transition ${currentQ.student_answer === option ? 'border-[var(--accent)] bg-[rgba(99,102,241,0.1)]' : 'border-[var(--border2)] bg-[rgba(255,255,255,0.03)] hover:border-[rgba(99,102,241,0.35)] hover:bg-[var(--accent-glow)]'}`}>
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 transition ${currentQ.student_answer === option ? 'bg-[var(--accent)] text-white border-[var(--accent)]' : 'bg-[rgba(255,255,255,0.06)] border border-[var(--border2)] text-[var(--text2)]'}`}>
                    {String.fromCharCode(65 + idx)}
                  </div>
                  <span className={`transition ${currentQ.student_answer === option ? 'text-[var(--text)]' : 'text-[var(--text2)]'}`}>{option}</span>
                </button>
              ))}
            </div>

            {/* Ask AI Component */}
            <AskAI
              sessionUuid={sessionUuid}
              questionIndex={currentQuestion}
              questionText={currentQ.question}
              onAIHelpUsed={(helpType) => handleAIHelpUsed(currentQuestion, helpType)}
              disabled={!sessionUuid}
            />

            <div className="mt-8 pt-6 border-t border-[var(--border)]">
              <div className="flex items-center justify-between">
                <button onClick={() => handleNavigateQuestion(-1)} disabled={currentQuestion === 0} className="flex items-center gap-2 px-5 py-2 rounded-lg bg-[rgba(255,255,255,0.05)] text-[var(--text2)] hover:text-[var(--text)] disabled:opacity-0 transition">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
                  Previous
                </button>
                <span className="text-xs text-[var(--text3)]">{currentQuestion + 1} / {questions.length}</span>
                <button onClick={() => handleNavigateQuestion(1)} disabled={currentQuestion === questions.length - 1} className="flex items-center gap-2 px-5 py-2 rounded-lg bg-[var(--accent)] text-white hover:bg-[var(--accent2)] disabled:hidden transition">
                  Next
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                </button>
              </div>
            </div>
          </div>

          <div className="flex gap-2 justify-center mb-8">
            {questions.map((q, idx) => (
              <button key={idx} onClick={() => setCurrentQuestion(idx)} className={`w-2 h-2 rounded-full transition ${q.student_answer ? 'bg-[var(--success)]' : idx === currentQuestion ? 'border border-[var(--accent)] scale-125' : 'bg-[rgba(255,255,255,0.1)] border border-[var(--border2)]'}`}></button>
            ))}
          </div>

          {currentQuestion === questions.length - 1 && (
            <form onSubmit={currentRound === 1 ? handleSubmitRound1 : handleSubmitRound2}>
              <div className="text-center text-sm text-[var(--text3)] mb-4">
                {unansweredCount > 0 ? (
                  <>Answer <strong className="text-[var(--accent2)]">{unansweredCount} more question{unansweredCount !== 1 ? 's' : ''}</strong> to submit</>
                ) : (
                  <>All questions answered — ready to submit!</>
                )}
              </div>
              <button type="submit" disabled={unansweredCount > 0 || loading} className="w-full px-6 py-3 bg-[var(--accent)] text-white font-semibold rounded-lg hover:bg-[var(--accent2)] disabled:opacity-40 transition flex items-center justify-center gap-2">
                {loading ? 'Analysing...' : `Submit Round ${currentRound} — Analyse My Answers`}
                {!loading && <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/></svg>}
              </button>
            </form>
          )}
        </div>
      </div>
    );
  }

  // Results screen
  if (result) {
    return (
      <div className="relative">
        <ResultsDashboard
          studentName={studentName}
          topic={topic}
          evaluation={result.round === 2 ? (result.round_2_evaluation!) : (result.evaluation!)}
          round1Evaluation={result.round === 2 ? result.round_1_evaluation : undefined}
          round1Score={result.round_1_score}
          generatedContent={result.generated_content}
          roadmap={result.roadmap}
          questions={result.questions || []}
          round={result.round}
        />
        <div className="fixed bottom-0 left-0 right-0 z-40 bg-gradient-to-t from-[var(--bg)] via-[var(--bg)]/80 to-transparent p-8 text-center">
          <button onClick={handleReset} className="w-full max-w-md mx-auto block px-8 py-4 bg-[var(--accent)] text-white font-semibold rounded-lg hover:bg-[var(--accent2)] transition">
            Start New Assessment
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default QuizPage;
