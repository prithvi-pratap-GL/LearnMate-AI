import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Starfield animation
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

    let stars: Star[] = Array.from({ length: 200 }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.4 + 0.2,
      o: Math.random() * 0.7 + 0.1,
      tw: Math.random() * Math.PI * 2,
      ts: Math.random() * 0.02 + 0.005,
      spd: Math.random() * 0.12 + 0.02
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

  // Scroll reveal observer
  useEffect(() => {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          (entry.target as HTMLElement).style.opacity = '1';
          (entry.target as HTMLElement).style.transform = 'none';
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('[data-reveal]').forEach((el) => {
      (el as HTMLElement).style.opacity = '0';
      (el as HTMLElement).style.transform = 'translateY(24px)';
      (el as HTMLElement).style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  return (
    <div className="relative overflow-hidden">
      <canvas ref={canvasRef} className="fixed inset-0 z-0 pointer-events-none" />

      {/* Glow blobs */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute w-96 h-96 rounded-full blur-3xl opacity-5" style={{ background: 'rgba(99, 102, 241, 0.2)', top: '-100px', left: '-100px' }} />
        <div className="absolute w-96 h-96 rounded-full blur-3xl opacity-5" style={{ background: 'rgba(139, 92, 246, 0.1)', bottom: '-100px', right: '-100px' }} />
      </div>

      <div className="relative z-10">
        {/* Navbar */}
        <nav className="sticky top-0 z-50 backdrop-blur-md border-b border-[var(--border)] bg-[rgba(10,10,15,0.7)]">
          <div className="max-w-6xl mx-auto px-8 h-16 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2 font-bold text-lg">
              <div className="w-8 h-8 bg-[var(--accent)] rounded flex items-center justify-center">
                <svg className="w-4 h-4 fill-white" viewBox="0 0 24 24"><path d="M13 2L4.09 12.26c-.36.44-.55.66-.55.88 0 .2.08.39.21.53.15.16.36.33.88.33H12l-1 8 8.91-10.26c.36-.44.55-.66.55-.88a.72.72 0 0 0-.21-.53c-.15-.16-.36-.33-.88-.33H13l1-8z"/></svg>
              </div>
              LearnMate AI
            </a>
            <div className="flex items-center gap-8">
              <a href="#how-it-works" className="text-sm text-[var(--text2)] hover:text-[var(--text)]">How it works</a>
              <a href="#features" className="text-sm text-[var(--text2)] hover:text-[var(--text)]">Features</a>
              <a href="#" className="text-sm text-[var(--text2)] hover:text-[var(--text)]">GitHub ↗</a>
              <Link to="/quiz" className="text-sm font-medium px-4 py-2 bg-[var(--accent)] text-white rounded hover:bg-[var(--accent2)] transition">
                Start Assessment
              </Link>
            </div>
          </div>
        </nav>

        {/* Hero */}
        <section className="min-h-screen flex items-center justify-center px-6 py-20">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--accent-glow)] border border-[rgba(99,102,241,0.3)] mb-8">
              <span className="w-2 h-2 rounded-full bg-[var(--accent2)] animate-pulse"></span>
              <span className="text-sm font-medium text-[var(--accent2)]">AI-powered adaptive learning</span>
            </div>

            <h1 className="text-6xl md:text-7xl font-bold leading-tight mb-6" style={{ fontFamily: 'Syne' }}>
              Master Any Topic<br/>with <span className="text-[var(--accent2)]">Adaptive AI</span> Quizzing
            </h1>

            <p className="text-lg text-[var(--text2)] mb-12 max-w-xl mx-auto leading-relaxed">
              Get assessed in two progressive rounds, receive AI-generated feedback, and walk away with a personalised learning roadmap built just for you.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-20">
              <Link to="/quiz" className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-[var(--accent)] text-white font-semibold rounded-lg hover:bg-[var(--accent2)] transition hover:shadow-lg hover:shadow-[rgba(99,102,241,0.3)]">
                Start Learning
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </Link>
              <button className="inline-flex items-center justify-center gap-2 px-8 py-4 border border-[var(--border2)] text-[var(--text2)] font-semibold rounded-lg hover:bg-[rgba(255,255,255,0.04)] transition">
                See how it works
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-3xl font-bold text-[var(--text)]" style={{ fontFamily: 'Syne' }}>2</div>
                <div className="text-xs text-[var(--text3)] mt-2">Adaptive rounds</div>
              </div>
              <div className="hidden md:block h-8 border-l border-[var(--border)]"></div>
              <div>
                <div className="text-3xl font-bold text-[var(--text)]" style={{ fontFamily: 'Syne' }}>10+</div>
                <div className="text-xs text-[var(--text3)] mt-2">Questions per session</div>
              </div>
              <div className="hidden md:block h-8 border-l border-[var(--border)]"></div>
              <div>
                <div className="text-3xl font-bold text-[var(--text)]" style={{ fontFamily: 'Syne' }}>∞</div>
                <div className="text-xs text-[var(--text3)] mt-2">Topics supported</div>
              </div>
              <div className="hidden md:block h-8 border-l border-[var(--border)]"></div>
              <div>
                <div className="text-3xl font-bold text-[var(--text)]" style={{ fontFamily: 'Syne' }}>AI</div>
                <div className="text-xs text-[var(--text3)] mt-2">Personalised roadmap</div>
              </div>
            </div>
          </div>
        </section>

        {/* How it works */}
        <section id="how-it-works" className="px-6 py-20" data-reveal>
          <div className="max-w-5xl mx-auto">
            <div className="mb-16">
              <div className="text-xs font-bold text-[var(--accent2)] tracking-wider uppercase mb-4">Process</div>
              <h2 className="text-4xl font-bold mb-4" style={{ fontFamily: 'Syne' }}>Three steps to mastery</h2>
              <p className="text-[var(--text2)] max-w-lg">From topic input to personalised roadmap in minutes. No setup, no account needed.</p>
            </div>

            <div className="grid md:grid-cols-3 gap-px bg-[var(--border)] rounded-2xl overflow-hidden">
              {[
                { num: '01', title: 'Choose your topic', desc: 'Enter any subject — Python, Machine Learning, System Design, SQL — and the AI generates a tailored question set instantly.' },
                { num: '02', title: 'Complete adaptive rounds', desc: 'Round 1 tests your foundations. Score ≥50% to unlock the advanced Round 2 — questions that push deeper into concepts.' },
                { num: '03', title: 'Get your roadmap', desc: 'Receive a detailed analytics dashboard with score breakdown, answer review, AI analysis, and a 30-day personalised learning roadmap.' }
              ].map((step, idx) => (
                <div key={idx} className="bg-[var(--surface)] p-10 relative">
                  <div className="text-5xl font-bold text-[rgba(255,255,255,0.04)] mb-6" style={{ fontFamily: 'Syne' }}>{step.num}</div>
                  <div className="w-12 h-12 rounded-lg bg-[var(--accent-glow)] border border-[rgba(99,102,241,0.25)] flex items-center justify-center mb-6">
                    {idx === 0 && <svg className="w-6 h-6 stroke-[var(--accent2)]" fill="none" strokeWidth="1.8" viewBox="0 0 24 24"><path d="M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>}
                    {idx === 1 && <svg className="w-6 h-6 stroke-[var(--accent2)]" fill="none" strokeWidth="1.8" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/></svg>}
                    {idx === 2 && <svg className="w-6 h-6 stroke-[var(--accent2)]" fill="none" strokeWidth="1.8" viewBox="0 0 24 24"><path d="M9 19v-6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2zm0 0V9a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v10m-6 0a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2m0 0V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2z"/></svg>}
                  </div>
                  <h3 className="font-bold text-lg mb-3">{step.title}</h3>
                  <p className="text-sm text-[var(--text2)] leading-relaxed">{step.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="px-6 py-20" data-reveal>
          <div className="max-w-5xl mx-auto">
            <div className="mb-16">
              <div className="text-xs font-bold text-[var(--accent2)] tracking-wider uppercase mb-4">Features</div>
              <h2 className="text-4xl font-bold mb-4" style={{ fontFamily: 'Syne' }}>Everything you need to level up</h2>
              <p className="text-[var(--text2)] max-w-lg">Built on top of state-of-the-art language models with safety guardrails baked in.</p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { icon: '⚡', title: 'AI-generated questions', desc: 'Every quiz is freshly generated by an LLM, validated for accuracy, and tailored to your chosen difficulty level.' },
                { icon: '📊', title: 'Performance analytics', desc: 'Visual score rings, strength/weakness breakdowns, and per-question answer reviews in a clean dashboard.' },
                { icon: '🗺️', title: 'Personalised roadmap', desc: 'A 30-day learning plan generated from your exact results — strengths, weak areas, and current proficiency level.' },
                { icon: '🛡️', title: 'AI safety guardrails', desc: 'Prompt injection detection, toxicity filtering, and PII redaction protect every request to the model.' }
              ].map((feature, idx) => (
                <div key={idx} className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl p-8 hover:border-[rgba(99,102,241,0.3)] hover:bg-[var(--surface2)] transition">
                  <div className="text-3xl mb-4">{feature.icon}</div>
                  <h3 className="font-bold text-lg mb-2">{feature.title}</h3>
                  <p className="text-sm text-[var(--text2)] leading-relaxed">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Banner */}
        <section className="px-6 py-20" data-reveal>
          <div className="max-w-2xl mx-auto bg-gradient-to-br from-[rgba(99,102,241,0.15)] to-[rgba(139,92,246,0.1)] border border-[rgba(99,102,241,0.25)] rounded-3xl p-16 text-center relative overflow-hidden">
            <div className="absolute w-96 h-96 rounded-full blur-3xl bg-[rgba(99,102,241,0.08)] -top-32 -right-32 pointer-events-none"></div>
            <div className="relative z-10">
              <h2 className="text-4xl font-bold mb-6" style={{ fontFamily: 'Syne' }}>Ready to find your knowledge gaps?</h2>
              <p className="text-[var(--text2)] mb-10">Takes less than 10 minutes. No account required. Start with any topic.</p>
              <Link to="/quiz" className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-[var(--accent)] text-white font-semibold rounded-lg hover:bg-[var(--accent2)] transition hover:shadow-lg hover:shadow-[rgba(99,102,241,0.3)]">
                Start Your Assessment
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </Link>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-[var(--border)] px-6 py-12">
          <div className="max-w-6xl mx-auto flex justify-between items-center">
            <div className="font-bold">LearnMate AI</div>
            <div className="text-sm text-[var(--text3)]">Powered by HuggingFace LLMs · Built with FastAPI + React</div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default HomePage;
