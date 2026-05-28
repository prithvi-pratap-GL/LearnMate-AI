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
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }}>
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
      <text
        x={size / 2}
        y={size / 2}
        textAnchor="middle"
        dominantBaseline="middle"
        className="text-xl font-bold fill-[var(--text)]"
        fontSize="32"
        fontFamily="Syne"
        style={{ transform: 'rotate(90deg)', transformOrigin: `${size / 2}px ${size / 2}px` }}
      >
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

  // Parse markdown formatting: bold (**text**), italic (*text*), remove them for display
  const parseMarkdown = (text: string) => {
    if (!text) return '';
    // Remove markdown formatting, keep the text
    let result = text
      .replace(/\*\*(.+?)\*\*/g, '$1')    // **bold** -> bold (non-greedy)
      .replace(/\*([^*]+?)\*/g, '$1')     // *italic* -> italic (but not ** which we already handled)
      .replace(/^#+\s+/, '');             // Remove heading markers from start
    return result.trim();
  };

  // AI Analysis rendering
  return (
    <div className="space-y-4">
      {lines.map((line, idx) => {
        const trimmed = line.trim();

        if (trimmed.startsWith('###')) {
          const title = trimmed.replace(/^#+\s*/, '');
          return (
            <div key={idx} className="mt-4 mb-2">
              <h4 className="text-base font-semibold text-[var(--accent2)]" style={{ fontFamily: 'Syne' }}>
                {parseMarkdown(title)}
              </h4>
            </div>
          );
        }

        if (trimmed.startsWith('##')) {
          const title = trimmed.replace(/^#+\s*/, '');
          return (
            <div key={idx} className="mt-6 mb-4">
              <h3 className="text-lg font-bold text-[var(--text)]" style={{ fontFamily: 'Syne' }}>
                {parseMarkdown(title)}
              </h3>
              <div className="h-1 w-12 bg-[var(--accent)] rounded mt-2"></div>
            </div>
          );
        }

        if (trimmed.startsWith('+') || trimmed.startsWith('-') || trimmed.startsWith('•')) {
          const cleaned = trimmed.replace(/^[+•-]\s*/, '');
          return (
            <div key={idx} className="flex items-start gap-3 ml-2">
              <span className="text-[var(--accent)] font-bold mt-1 flex-shrink-0">+</span>
              <p className="text-sm text-[var(--text2)] leading-relaxed">
                {parseMarkdown(cleaned)}
              </p>
            </div>
          );
        }

        if (trimmed && !trimmed.match(/^#+/) && !trimmed.match(/^[*\s]/)) {
          return (
            <p key={idx} className="text-sm text-[var(--text2)] leading-relaxed">
              {parseMarkdown(trimmed)}
            </p>
          );
        }

        return null;
      })}
    </div>
  );
};

// Structured AI Analysis Panel
const AnalysisPanel: React.FC<{ content: string }> = ({ content }) => {
  const lines = content.split('\n').filter(line => line.trim());

  // Extract sections from content
  let currentSection = '';
  const allSections: { [key: string]: string[] } = {};

  lines.forEach(line => {
    const trimmed = line.trim();
    if (trimmed.startsWith('##') || trimmed.startsWith('###')) {
      currentSection = trimmed.replace(/^#+\s*/, '').toLowerCase();
      allSections[currentSection] = [];
    } else if (trimmed && currentSection) {
      allSections[currentSection].push(trimmed.replace(/^\*+/, '').replace(/^\*+/, '').replace(/^[-•]\s*/, '').trim());
    }
  });

  // Extract key insights
  const strengths = allSections['strengths'] || allSections['strength'] || [];
  const weaknesses = allSections['weak areas'] || allSections['weaknesses'] || allSections['areas to improve'] || [];

  // Build analysis summary from content
  const summaryLines = lines.slice(0, Math.min(3, lines.length)).filter(l => !l.startsWith('#'));
  const summary = summaryLines.join(' ').substring(0, 200);

  return (
    <div className="space-y-6">
      {/* Performance Summary */}
      <div className="bg-[var(--accent)]/10 border border-[var(--accent)]/25 rounded-xl p-6">
        <h4 className="text-sm font-bold text-[var(--accent)] mb-3">Performance Summary</h4>
        <p className="text-sm text-[var(--text2)] leading-relaxed">
          {summary || 'Your performance demonstrates a solid understanding of the core concepts with room for improvement in specific areas.'}
        </p>
      </div>

      {/* Strengths Section */}
      <div>
        <h4 className="text-sm font-bold text-[var(--success)] mb-4 flex items-center gap-2">
          <span>✓</span> Key Strengths
        </h4>
        <div className="grid gap-2">
          {strengths && strengths.length > 0 ? (
            strengths.slice(0, 4).map((item, idx) => (
              <div key={idx} className="flex items-start gap-3 px-4 py-3 rounded-lg bg-[var(--success-bg)]/30 border border-[var(--success)]/20">
                <span className="text-[var(--success)] text-sm mt-0.5 flex-shrink-0">●</span>
                <p className="text-sm text-[var(--text2)]">{item}</p>
              </div>
            ))
          ) : (
            <div className="text-sm text-[var(--text3)]">Strong understanding demonstrated across topics</div>
          )}
        </div>
      </div>

      {/* Weak Areas Section */}
      <div>
        <h4 className="text-sm font-bold text-[var(--warning)] mb-4 flex items-center gap-2">
          <span>!</span> Areas for Focus
        </h4>
        <div className="grid gap-2">
          {weaknesses && weaknesses.length > 0 ? (
            weaknesses.slice(0, 4).map((item, idx) => (
              <div key={idx} className="flex items-start gap-3 px-4 py-3 rounded-lg bg-[var(--warning-bg)]/30 border border-[var(--warning)]/20">
                <span className="text-[var(--warning)] text-sm mt-0.5 flex-shrink-0">→</span>
                <p className="text-sm text-[var(--text2)]">{item}</p>
              </div>
            ))
          ) : (
            <div className="text-sm text-[var(--text3)]">Focus on deepening understanding through practice</div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-gradient-to-r from-[var(--accent)]/5 to-[var(--accent2)]/5 border border-[var(--accent)]/20 rounded-xl p-6">
        <h4 className="text-sm font-bold text-[var(--accent2)] mb-3">Next Steps</h4>
        <ul className="space-y-2">
          <li className="flex items-start gap-3 text-sm text-[var(--text2)]">
            <span className="text-[var(--accent)] flex-shrink-0">→</span>
            <span>Review the weak areas using the Learning Roadmap</span>
          </li>
          <li className="flex items-start gap-3 text-sm text-[var(--text2)]">
            <span className="text-[var(--accent)] flex-shrink-0">→</span>
            <span>Practice similar questions to strengthen understanding</span>
          </li>
          <li className="flex items-start gap-3 text-sm text-[var(--text2)]">
            <span className="text-[var(--accent)] flex-shrink-0">→</span>
            <span>Take another assessment to track your progress</span>
          </li>
        </ul>
      </div>
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

          {/* Score Cards - Always 3-column layout */}
          <div className="grid lg:grid-cols-3 gap-6 mb-12">
            {/* Card 1: Foundations (Round 1) */}
            <div className="bg-[var(--surface)] border border-[var(--border2)] rounded-2xl p-8 text-center">
              <div className="text-xs uppercase tracking-widest text-[var(--text3)] font-bold mb-6">Foundations</div>
              <ScoreRing score={round === 2 && round1Score !== undefined ? round1Score : evaluation.score} size={140} />
              <div className="mt-6">
                <div className="text-sm text-[var(--text2)] mb-2">Progression</div>
                <div className="text-xs font-bold text-[var(--text)]">
                  {round === 2
                    ? (round1Evaluation?.level ? getLevelArrow('Beginner', round1Evaluation.level) : 'Beginner → Intermediate')
                    : 'Beginner → ' + (evaluation.level || 'Intermediate')}
                </div>
                <div className={`mt-3 text-xs px-3 py-1 rounded-full inline-block font-bold ${getLevelColor(round === 2 ? (round1Evaluation?.level || '') : evaluation.level)}`}>
                  {round === 2 ? (round1Evaluation?.level || 'Beginner') : evaluation.level}
                </div>
              </div>
            </div>

            {/* Card 2: Advanced (Round 2) */}
            <div className="bg-[var(--surface)] border border-[var(--border2)] rounded-2xl p-8 text-center">
              <div className="text-xs uppercase tracking-widest text-[var(--text3)] font-bold mb-6">Advanced</div>
              <ScoreRing score={round === 2 ? evaluation.score : 0} size={140} />
              <div className="mt-6">
                <div className="text-sm text-[var(--text2)] mb-2">Progression</div>
                <div className="text-xs font-bold text-[var(--text)] mb-3">
                  {round === 2 ? 'Intermediate → Advanced' : 'Not Available'}
                </div>
              </div>
              <div className={`mt-3 text-xs px-3 py-1 rounded-full inline-block font-bold ${round === 2 ? getLevelColor(evaluation.level) : 'text-[var(--text3)]'}`}>
                {round === 2 ? evaluation.level : '—'}
              </div>
            </div>

            {/* Card 3: Score Comparison */}
            <div className="bg-[var(--surface)] border border-[var(--border2)] rounded-2xl p-8">
              <div className="text-xs uppercase tracking-widest text-[var(--text3)] font-bold mb-8">Score Comparison</div>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">Round 1</span>
                    <span className="text-sm font-bold text-[var(--text)]">{round === 2 && round1Score !== undefined ? round1Score : evaluation.score}%</span>
                  </div>
                  <div className="h-2 bg-[rgba(255,255,255,0.08)] rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500" style={{ width: `${round === 2 && round1Score !== undefined ? round1Score : evaluation.score}%` }}></div>
                  </div>
                </div>
                {round === 2 && (
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Round 2</span>
                      <span className="text-sm font-bold text-[var(--text)]">{evaluation.score}%</span>
                    </div>
                    <div className="h-2 bg-[rgba(255,255,255,0.08)] rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: `${evaluation.score}%` }}></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
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
                    {evaluation.strengths && evaluation.strengths.length > 0 ? (
                      evaluation.strengths.map((str, idx) => (
                        <div key={idx} className="flex items-center gap-3 px-4 py-3 rounded-lg bg-[var(--success-bg)] border border-[var(--success-border)]">
                          <span className="text-[var(--success)]">●</span>
                          <span className="text-sm text-[var(--text)]">{str}</span>
                        </div>
                      ))
                    ) : (
                      <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-[var(--success-bg)] border border-[var(--success-border)]">
                        <span className="text-[var(--success)]">✓</span>
                        <span className="text-sm text-[var(--text)]">Great effort! Keep learning and improving 🚀</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="bg-[var(--surface2)] border border-[var(--border)] rounded-2xl p-8">
                  <h3 className="font-bold text-lg mb-6 flex items-center gap-2">
                    <span className="text-2xl">!</span> Areas to Improve
                  </h3>
                  <div className="space-y-3">
                    {evaluation.weak_areas && evaluation.weak_areas.length > 0 ? (
                      evaluation.weak_areas.map((area, idx) => (
                        <div key={idx} className="flex items-center gap-3 px-4 py-3 rounded-lg bg-[var(--warning-bg)] border border-[var(--warning-border)]">
                          <span className="text-[var(--warning)]">●</span>
                          <span className="text-sm text-[var(--text)]">{area}</span>
                        </div>
                      ))
                    ) : (
                      <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-[var(--accent-glow)] border border-[rgba(99,102,241,0.25)]">
                        <span className="text-[var(--accent)]">✓</span>
                        <span className="text-sm text-[var(--text)]">No weaknesses identified. You're doing excellent! 🌟</span>
                      </div>
                    )}
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
                {generatedContent && generatedContent.content ? (
                  <AnalysisPanel content={generatedContent.content + '\n## Strengths\n' + (evaluation.strengths || []).map(s => `- ${s}`).join('\n') + '\n## Weak Areas\n' + (evaluation.weak_areas || []).map(w => `- ${w}`).join('\n')} />
                ) : (
                  <p className="text-[var(--text2)]">AI analysis is being generated...</p>
                )}
              </div>
            )}

            {/* Roadmap Tab */}
            {activeTab === 'roadmap' && (
              <div className="bg-[var(--surface2)] border border-[var(--border)] rounded-2xl p-8">
                {roadmap && roadmap.content ? (
                  <StructuredContent content={roadmap.content} isRoadmap />
                ) : (
                  <p className="text-[var(--text2)]">Personalized learning roadmap will be generated based on your performance...</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsDashboard;
