import React, { useState, useEffect, useRef } from 'react';
import type { IQuestion, IEvaluation, IGeneratedContent, IRoadmap } from '../types';

interface IResultsDashboardProps {
  studentName: string;
  topic: string;
  evaluation: IEvaluation;
  round1Evaluation?: IEvaluation;
  round1Score?: number;
  generatedContent: IGeneratedContent;
  roadmap: IRoadmap;
  questions: IQuestion[];
  round: number;
}

// SVG Score Ring component
const ScoreRing: React.FC<{ score: number; size?: number }> = ({ score, size = 140 }) => {
  const circumference = 2 * Math.PI * (size / 2 - 18);
  const offset = circumference - (score / 100) * circumference;

  return (
    <svg width={size} height={size} className="transform -rotate-90">
      <circle cx={size / 2} cy={size / 2} r={size / 2 - 18} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="6" />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={size / 2 - 18}
        fill="none"
        stroke="#6366f1"
        strokeWidth="6"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        className="transition-[stroke-dashoffset] duration-1000 ease-out"
      />
      <text x={size / 2} y={size / 2 + 8} textAnchor="middle" className="text-xl font-bold fill-[var(--text)]" fontSize="32" fontFamily="Syne">
        {score}%
      </text>
    </svg>
  );
};

// Starfield background
const Starfield: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
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

    let stars: Star[] = Array.from({ length: 150 }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.2 + 0.2,
      o: Math.random() * 0.5 + 0.1,
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
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 z-0 pointer-events-none" />;
};

// Content parser for better rendering
const StructuredContent: React.FC<{ content: string; isRoadmap?: boolean }> = ({ content, isRoadmap }) => {
  const lines = content.split('\n').filter(line => line.trim());

  if (isRoadmap) {
    // Parse roadmap into structured steps
    const steps: Array<{ title: string; items: string[] }> = [];
    let currentStep: { title: string; items: string[] } | null = null;

    lines.forEach(line => {
      const trimmed = line.trim();
      // Match day headers like "Day 1-2" or "Day 1"
      if (/^Day \d+/.test(trimmed) || trimmed.match(/^Week \d+/)) {
        if (currentStep) steps.push(currentStep);
        const titleMatch = trimmed.match(/^(Day \d+[\d\-]*.*|Week \d+.*)/);
        currentStep = {
          title: titleMatch ? titleMatch[1] : trimmed,
          items: []
        };
      } else if (trimmed.startsWith('-') || trimmed.startsWith('•')) {
        if (currentStep) {
          currentStep.items.push(trimmed.replace(/^[-•]\s*/, ''));
        }
      } else if (trimmed && currentStep) {
        // Add non-list items as items
        if (!trimmed.startsWith('##') && !trimmed.startsWith('###')) {
          currentStep.items.push(trimmed);
        }
      }
    });

    if (currentStep) steps.push(currentStep);

    return (
      <div className="space-y-4">
        {steps.map((step, idx) => (
          <div key={idx} className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className="w-10 h-10 rounded-full bg-[var(--accent)] flex items-center justify-center text-white font-bold text-sm" style={{ fontFamily: 'Syne' }}>
                {idx + 1}
              </div>
              {idx < steps.length - 1 && <div className="w-1 h-12 bg-gradient-to-b from-[var(--accent)] to-transparent mt-2"></div>}
            </div>
            <div className="flex-1 pt-1">
              <h4 className="font-bold text-sm text-[var(--text)] mb-3">{step.title}</h4>
              <ul className="space-y-2">
                {step.items.map((item, itemIdx) => (
                  <li key={itemIdx} className="flex items-start gap-3 text-sm text-[var(--text2)]">
                    <span className="text-[var(--accent)] mt-0.5">→</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // AI Analysis rendering
  return (
    <div className="space-y-4">
      {lines.map((line, idx) => {
        const trimmed = line.trim();

        if (trimmed.startsWith('##')) {
          const title = trimmed.replace(/^#+\s*/, '');
          return (
            <div key={idx} className="mt-6 mb-4">
              <h3 className="text-lg font-bold text-[var(--text)]" style={{ fontFamily: 'Syne' }}>
                {title}
              </h3>
              <div className="h-1 w-12 bg-[var(--accent)] rounded mt-2"></div>
            </div>
          );
        }

        if (trimmed.startsWith('-') || trimmed.startsWith('•')) {
          return (
            <div key={idx} className="flex items-start gap-3">
              <span className="text-[var(--accent)] font-bold mt-1">●</span>
              <p className="text-sm text-[var(--text2)] leading-relaxed">
                {trimmed.replace(/^[-•]\s*/, '')}
              </p>
            </div>
          );
        }

        if (trimmed) {
          return (
            <p key={idx} className="text-sm text-[var(--text2)] leading-relaxed">
              {trimmed}
            </p>
          );
        }

        return null;
      })}
    </div>
  );
};

const ResultsDashboard: React.FC<IResultsDashboardProps> = ({
  studentName,
  topic,
  evaluation,
  round1Evaluation,
  round1Score,
  generatedContent,
  roadmap,
  questions,
  round
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'answers' | 'analysis' | 'roadmap'>('overview');
  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(null);

  const isAnswerCorrect = (correct: string, student: string) =>
    correct.toLowerCase().trim() === student.toLowerCase().trim();

  const getLevelColor = (level: string) => {
    if (level.includes('Beginner')) return 'text-blue-400';
    if (level.includes('Intermediate')) return 'text-yellow-400';
    if (level.includes('Advanced')) return 'text-green-400';
    return 'text-[var(--accent2)]';
  };

  const getLevelArrow = (from: string, to: string) => `${from} → ${to}`;

  return (
    <div className="fixed inset-0 bg-[var(--bg)] overflow-y-auto">
      <Starfield />

      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute w-96 h-96 rounded-full blur-3xl opacity-5" style={{ background: 'rgba(99, 102, 241, 0.2)', top: '-50px', left: '-100px' }} />
        <div className="absolute w-96 h-96 rounded-full blur-3xl opacity-5" style={{ background: 'rgba(139, 92, 246, 0.1)', bottom: '-100px', right: '-100px' }} />
      </div>

      <div className="relative z-10">
        {/* Navbar */}
        <nav className="sticky top-0 z-50 backdrop-blur-md border-b border-[var(--border)] bg-[rgba(10,10,15,0.8)]">
          <div className="max-w-6xl mx-auto px-8 h-16 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2 font-bold">
              <div className="w-7 h-7 bg-[var(--accent)] rounded flex items-center justify-center">
                <svg className="w-3.5 h-3.5 fill-white" viewBox="0 0 24 24"><path d="M13 2L4.09 12.26c-.36.44-.55.66-.55.88 0 .2.08.39.21.53.15.16.36.33.88.33H12l-1 8 8.91-10.26c.36-.44.55-.66.55-.88a.72.72 0 0 0-.21-.53c-.15-.16-.36-.33-.88-.33H13l1-8z"/></svg>
              </div>
              LearnMate AI
            </a>
            <a href="/quiz" className="text-sm font-medium px-4 py-2 bg-[var(--accent)] text-white rounded hover:bg-[var(--accent2)] transition">
              + New Assessment
            </a>
          </div>
        </nav>

        <div className="max-w-6xl mx-auto px-8 py-12">
          {/* Header */}
          <div className="mb-12">
            <h1 className="text-5xl font-bold mb-2" style={{ fontFamily: 'Syne' }}>Assessment Complete, {studentName}</h1>
            <p className="text-[var(--text2)] mb-6">Here's your personalised performance breakdown and learning roadmap</p>
            <div className="flex gap-3">
              <span className="text-xs px-3 py-1.5 rounded-full bg-[var(--accent-glow)] border border-[rgba(99,102,241,0.25)] text-[var(--accent2)]">{topic}</span>
              <span className="text-xs px-3 py-1.5 rounded-full bg-[rgba(255,255,255,0.05)] border border-[var(--border2)] text-[var(--text2)]">
                {round === 2 ? 'Round 1 + Round 2' : 'Round 1'}
              </span>
            </div>
          </div>

          {/* Score Cards */}
          <div className={`grid ${round === 2 ? 'lg:grid-cols-3' : 'lg:grid-cols-1'} gap-6 mb-12`}>
            {round === 2 && round1Score !== undefined && (
              <div className="bg-[var(--surface)] border border-[var(--border2)] rounded-2xl p-8 text-center">
                <div className="text-xs uppercase tracking-widest text-[var(--text3)] font-bold mb-6">Foundations</div>
                <ScoreRing score={round1Score} size={140} />
                <div className="mt-6">
                  <div className="text-sm text-[var(--text2)] mb-2">Progression</div>
                  <div className="text-xs font-bold text-[var(--text)]">
                    {round1Evaluation?.level ? getLevelArrow('Beginner', round1Evaluation.level) : 'Beginner → Intermediate'}
                  </div>
                  <div className={`mt-3 text-xs px-3 py-1 rounded-full inline-block font-bold ${getLevelColor(round1Evaluation?.level || '')}`}>
                    {round1Evaluation?.level || 'Beginner'}
                  </div>
                </div>
              </div>
            )}

            <div className={`bg-[var(--surface)] border border-[var(--border2)] rounded-2xl p-8 text-center ${round === 2 ? '' : 'lg:col-span-1'}`}>
              <div className="text-xs uppercase tracking-widest text-[var(--text3)] font-bold mb-6">
                {round === 2 ? 'Advanced' : 'Your Score'}
              </div>
              <ScoreRing score={evaluation.score} size={140} />
              <div className="mt-6">
                {round === 2 && (
                  <div>
                    <div className="text-sm text-[var(--text2)] mb-2">Progression</div>
                    <div className="text-xs font-bold text-[var(--text)] mb-3">
                      Intermediate → Advanced
                    </div>
                  </div>
                )}
                <div className={`mt-3 text-xs px-3 py-1 rounded-full inline-block font-bold ${getLevelColor(evaluation.level)}`}>
                  {evaluation.level}
                </div>
              </div>
            </div>

            {round === 2 && (
              <div className="bg-[var(--surface)] border border-[var(--border2)] rounded-2xl p-8">
                <div className="text-xs uppercase tracking-widest text-[var(--text3)] font-bold mb-8">Score comparison</div>
                <div className="space-y-6">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Round 1</span>
                      <span className="text-sm font-bold text-[var(--text)]">{round1Score}%</span>
                    </div>
                    <div className="h-2 bg-[rgba(255,255,255,0.08)] rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500" style={{ width: `${round1Score}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Round 2</span>
                      <span className="text-sm font-bold text-[var(--text)]">{evaluation.score}%</span>
                    </div>
                    <div className="h-2 bg-[rgba(255,255,255,0.08)] rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: `${evaluation.score}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Tabs */}
          <div className="mb-8">
            <div className="flex gap-1 mb-6 bg-[var(--surface)] p-1 rounded-xl border border-[var(--border)]">
              {[
                { id: 'overview' as const, label: '📊 Overview' },
                { id: 'answers' as const, label: '✍️ Answer Review' },
                { id: 'analysis' as const, label: '💭 AI Analysis' },
                { id: 'roadmap' as const, label: '🗺️ Learning Roadmap' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 px-4 py-3 rounded-lg font-medium text-sm transition ${
                    activeTab === tab.id
                      ? 'bg-[var(--accent)] text-white'
                      : 'text-[var(--text2)] hover:text-[var(--text)]'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-[var(--surface2)] border border-[var(--border)] rounded-2xl p-8">
                  <h3 className="font-bold text-lg mb-6 flex items-center gap-2">
                    <span className="text-2xl">✓</span> Strengths
                  </h3>
                  <div className="space-y-3">
                    {evaluation.strengths.map((str, idx) => (
                      <div key={idx} className="flex items-center gap-3 px-4 py-3 rounded-lg bg-[var(--success-bg)] border border-[var(--success-border)]">
                        <span className="text-[var(--success)]">●</span>
                        <span className="text-sm text-[var(--text)]">{str}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-[var(--surface2)] border border-[var(--border)] rounded-2xl p-8">
                  <h3 className="font-bold text-lg mb-6 flex items-center gap-2">
                    <span className="text-2xl">!</span> Areas to Improve
                  </h3>
                  <div className="space-y-3">
                    {evaluation.weak_areas.map((area, idx) => (
                      <div key={idx} className="flex items-center gap-3 px-4 py-3 rounded-lg bg-[var(--warning-bg)] border border-[var(--warning-border)]">
                        <span className="text-[var(--warning)]">●</span>
                        <span className="text-sm text-[var(--text)]">{area}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Answer Review Tab */}
            {activeTab === 'answers' && (
              <div className="space-y-3">
                {questions.map((q, idx) => {
                  const correct = isAnswerCorrect(q.correct_answer, q.student_answer);
                  return (
                    <div key={idx} className="bg-[var(--surface)] border border-[var(--border2)] rounded-xl overflow-hidden">
                      <button
                        onClick={() => setExpandedQuestion(expandedQuestion === idx ? null : idx)}
                        className="w-full px-6 py-4 flex items-center justify-between hover:bg-[var(--surface2)] transition"
                      >
                        <div className="text-left">
                          <div className="font-medium text-sm mb-1">Question {idx + 1}</div>
                          <p className="text-sm text-[var(--text2)]">{q.question}</p>
                        </div>
                        <div className={`flex-shrink-0 ml-4 px-3 py-1 rounded-full text-xs font-bold ${correct ? 'bg-[var(--success-bg)] text-[var(--success)]' : 'bg-[var(--danger)]/10 text-[var(--danger)]'}`}>
                          {correct ? '✓ Correct' : '✗ Incorrect'}
                        </div>
                      </button>

                      {expandedQuestion === idx && (
                        <div className="border-t border-[var(--border)] px-6 py-4 bg-[rgba(255,255,255,0.02)]">
                          <div className="space-y-4">
                            <div>
                              <div className="text-xs font-bold text-[var(--text2)] uppercase tracking-wider mb-3">Options</div>
                              <div className="flex flex-wrap gap-2">
                                {q.options?.map((opt, optIdx) => {
                                  const isCorrectOpt = opt === q.correct_answer;
                                  const isStudentOpt = opt === q.student_answer;
                                  return (
                                    <span
                                      key={optIdx}
                                      className={`text-xs px-3 py-1.5 rounded-full border ${
                                        isCorrectOpt
                                          ? 'bg-[var(--success-bg)] border-[var(--success-border)] text-[var(--success)]'
                                          : isStudentOpt && !isCorrectOpt
                                          ? 'bg-[var(--danger)]/10 border-[var(--danger)]/25 text-[var(--danger)]'
                                          : 'bg-[rgba(255,255,255,0.03)] border-[var(--border)] text-[var(--text2)]'
                                      }`}
                                    >
                                      {opt}
                                    </span>
                                  );
                                })}
                              </div>
                            </div>
                            <div>
                              <div className="text-xs font-bold text-[var(--text2)] uppercase tracking-wider mb-2">Your Answer</div>
                              <span className={`text-xs px-3 py-1.5 rounded-full inline-block ${correct ? 'bg-[var(--success-bg)] border border-[var(--success-border)] text-[var(--success)]' : 'bg-[var(--danger)]/10 border border-[var(--danger)]/25 text-[var(--danger)]'}`}>
                                {q.student_answer}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* AI Analysis Tab */}
            {activeTab === 'analysis' && (
              <div className="bg-[var(--surface2)] border border-[var(--border)] rounded-2xl p-8">
                <StructuredContent content={generatedContent.content} />
              </div>
            )}

            {/* Roadmap Tab */}
            {activeTab === 'roadmap' && (
              <div className="bg-[var(--surface2)] border border-[var(--border)] rounded-2xl p-8">
                <StructuredContent content={roadmap.content} isRoadmap />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsDashboard;
