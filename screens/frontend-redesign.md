# LearnMate AI — Frontend Redesign Handover

> Hand this document to the LLM doing the redesign. It contains everything needed: what the app does, the exact data shapes from the backend, what screens exist, what the current code looks like, what to replace, and the design brief.

---

## 1. What This App Does

**LearnMate AI** is an AI-powered adaptive learning assessment platform. A user enters their name and a topic (e.g. "Python", "Machine Learning", "React"), then gets quizzed in two rounds. The AI evaluates their answers, generates a personalised performance analysis, and builds a learning roadmap.

### Flow

```
Landing Page
    ↓
Setup Screen (name + topic input)
    ↓
Round 1 — 5 beginner MCQ questions
    ↓
  Score < 50%?  ──→  Results Dashboard (Round 1 only: performance analysis + roadmap)
    ↓
  Score ≥ 50%
    ↓
Round 2 — 5 advanced MCQ questions
    ↓
Results Dashboard (full: R1 + R2 scores, answer review, solutions, roadmap)
```

---

## 2. Tech Stack (do not change)

| Layer | Technology |
|---|---|
| Framework | React 19 + TypeScript |
| Bundler | Vite |
| Styling | Tailwind CSS v4 |
| Routing | react-router-dom v7 |
| HTTP | axios |
| Toasts | react-hot-toast |
| CSS import | `@import "tailwindcss"` in `index.css` (Tailwind v4 style — no `@tailwind` directives) |

**Important Tailwind v4 note:** This project uses Tailwind v4. Do NOT use `@tailwind base/components/utilities`. The correct import is simply `@import "tailwindcss";` in the CSS file. All standard utility classes still work.

---

## 3. Project File Structure

```
frontend/
├── src/
│   ├── App.tsx                          ← Router setup (keep as-is)
│   ├── App.css                          ← Legacy Vite CSS (can be cleared)
│   ├── index.css                        ← Global styles + Tailwind import
│   ├── main.tsx                         ← Entry point (keep as-is)
│   ├── pages/
│   │   ├── HomePage.tsx                 ← REDESIGN
│   │   └── QuizPage.tsx                 ← REDESIGN (main logic lives here)
│   └── components/
│       ├── Layout.tsx                   ← REDESIGN (navbar + shell)
│       └── ResultsDashboard.tsx         ← REDESIGN (analytics dashboard)
├── index.html
├── vite.config.ts
├── tailwind.config.js                   ← mostly commented out, Tailwind v4 auto-config
└── package.json
```

You may add new files (e.g. `src/types.ts`, `src/components/ui/`, `src/hooks/`) freely.

---

## 4. TypeScript Types (extract to `src/types.ts`)

These interfaces are currently duplicated across files. Move them to a single `src/types.ts`:

```typescript
export interface IQuestion {
  question: string;
  correct_answer: string;
  student_answer: string;
  options?: string[];
}

export interface IEvaluation {
  score: number;           // 0–100
  strengths: string[];     // e.g. ["Strong grasp of closures", "Understands async"]
  weak_areas: string[];    // e.g. ["Prototype chain", "Memory management"]
  level: string;           // "Beginner" | "Intermediate" | "Advanced"
}

export interface IGeneratedContent {
  type: 'performance_analysis' | 'solution' | 'advanced_challenges';
  content: string;         // Markdown-like string with ##, ###, **, - list items
}

export interface IRoadmap {
  title: string;           // e.g. "Personalized Roadmap for Beginner"
  content: string;         // Markdown-like string (same format as above)
}

export interface IAnalysisResult {
  status: string;
  round: 1 | 2;
  evaluation?: IEvaluation;          // present on round 1 fail
  round_2_evaluation?: IEvaluation;  // present on round 2 complete
  generated_content: IGeneratedContent;
  roadmap: IRoadmap;
  questions?: IQuestion[];
  round_1_score?: number;            // present on round 2 complete
  can_proceed_to_round_2?: boolean;
}
```

---

## 5. Backend API

Base URL: `http://localhost:8000`

All requests are `POST`, JSON body, JSON response.

### 5.1 Generate Round 1 Questions
```
POST /api/learning/generate-questions
Body:  { "topic": string }
Response: {
  "questions": IQuestion[],   // always 5 items
  "round": 1,
  "total_questions": 5,
  "source": "llm" | "mock"
}
```

### 5.2 Submit Round 1
```
POST /api/learning/submit-round-1
Body: {
  "student_name": string,
  "topic": string,
  "questions": IQuestion[]
}
Response (pass, score ≥ 50): {
  "status": "proceed_to_round_2",
  "round": 1,
  "score": number,
  "evaluation": IEvaluation,
  "can_proceed_to_round_2": true
}
Response (fail, score < 50): {
  "status": "completed",
  "round": 1,
  "evaluation": IEvaluation,
  "generated_content": IGeneratedContent,
  "roadmap": IRoadmap,
  "can_proceed_to_round_2": false
}
```

### 5.3 Generate Round 2 Questions
```
POST /api/learning/generate-round-2-questions
Body: {
  "topic": string,
  "round_1_questions": IQuestion[]    // REQUIRED — used for deduplication
}
Response: {
  "questions": IQuestion[],           // up to 5 items
  "round": 2,
  "total_questions": number
}
```

### 5.4 Submit Round 2
```
POST /api/learning/submit-round-2
Body: {
  "student_name": string,
  "topic": string,
  "questions": IQuestion[],
  "round_1_score": number,
  "round_1_evaluation": IEvaluation,
  "round_1_questions": IQuestion[]
}
Response: {
  "status": "completed",
  "round": 2,
  "round_1_score": number,
  "round_2_evaluation": IEvaluation,
  "generated_content": IGeneratedContent,    // type: "solution"
  "roadmap": IRoadmap,
  "questions": IQuestion[]
}
```

### Error handling
On any API error, the backend returns `{ "detail": "..." }` with status 400 or 500.
- 400 = safety/validation error (e.g. prompt injection detected) — show the `detail` message to the user
- 500 = internal error — show generic retry message

---

## 6. State the QuizPage Must Manage

```typescript
studentName: string
topic: string
currentRound: 0 | 1 | 2       // 0 = setup screen
questions: IQuestion[]
loading: boolean               // true while submitting round
generatingQuestions: boolean   // true while fetching questions
error: string | null
result: IAnalysisResult | null
round1Evaluation: IEvaluation | null
round1Score: number | null
round1Questions: IQuestion[]   // needed for R2 dedup AND for showing R1 review on results
```

### Critical bug to fix
When calling "Generate Round 2 Questions", the current code sends `{ topic }` only. It **must** also send `round_1_questions: round1Questions` so the backend can deduplicate questions between rounds.

---

## 7. Current Code to Replace

### `App.tsx` — keep exactly as-is
```tsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import QuizPage from './pages/QuizPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="quiz" element={<QuizPage />} />
        </Route>
      </Routes>
    </Router>
  );
}
export default App;
```

### `Layout.tsx` — current (replace this)
Simple white navbar with "LearnMate AI" text link on left, no other nav items.

### `HomePage.tsx` — current (replace this)
Gray background, centered h1 + p + one purple button linking to `/quiz`. No features, no illustration, no copy.

### `QuizPage.tsx` — current (replace this)
- Setup screen: white card, two inputs (name, topic), blue button
- Quiz screen: plain white cards per question, radio buttons unstyled, no progress indicator
- Results passed to ResultsDashboard component

### `ResultsDashboard.tsx` — current (replace this)
- Score shown as a plain number (no chart, no ring, no visual)
- Strengths/weak areas as plain `<ul>` lists
- Generated content rendered as raw innerHTML from markdown-like string
- Roadmap rendered same way
- No tabs, no visual hierarchy, just stacked divs

---

## 8. Design Brief

### Aesthetic Direction
**"Dark-mode SaaS analytics dashboard"** — think Linear, Vercel dashboard, or Raycast. Clean, data-forward, high-contrast, minimal chrome. Dark background with vibrant accent colours. Professional and modern but not corporate-boring.

### Colour Palette (suggested, you may refine)
```
Background:     #0a0a0f   (near black)
Surface:        #111118   (card background)
Surface raised: #1a1a24   (elevated cards)
Border:         #2a2a3a   (subtle borders)
Accent:         #6366f1   (indigo — primary actions)
Accent hover:   #818cf8
Success:        #22c55e
Warning:        #f59e0b
Danger:         #ef4444
Text primary:   #f1f5f9
Text secondary: #94a3b8
Text muted:     #475569
```

### Typography
Use Google Fonts. Suggested pairing:
- Display / headings: **Syne** or **Plus Jakarta Sans** (bold, geometric)
- Body: **DM Sans** or **Outfit** (clean, readable)

Load via `<link>` in `index.html` or `@import` in CSS.

### Layout principles
- Max content width: `1100px`, centred
- Generous padding: `24px` mobile, `48px` desktop
- Cards with `border-radius: 12px` and `1px` borders (not box shadows)
- Subtle grain/noise texture on backgrounds (CSS `::before` with SVG noise or `background-image`)

---

## 9. Screen-by-Screen Requirements

### 9.1 Layout (navbar)
- Dark navbar, `LearnMate AI` logo left with a small lightning bolt or brain icon (inline SVG)
- Right side: subtle "GitHub" link (just visual, `href="#"`) and a "Start Assessment" button (accent colour)
- Sticky, `backdrop-filter: blur` when scrolled

### 9.2 HomePage
Must convey what the app does and create desire to start. Include:

**Hero section:**
- Large heading: "Master Any Topic with AI-Powered Adaptive Quizzing"
- Subheading about personalised assessments and learning roadmaps
- Two CTAs: "Start Learning →" (accent, goes to `/quiz`) + "See how it works" (ghost)
- Visual: an abstract animated element OR a mock screenshot of the dashboard (CSS-drawn, not image-dependent)

**How it works section** (3 steps, horizontal on desktop):
1. Choose a topic
2. Complete adaptive rounds
3. Get your personalised roadmap

**Features section** (3–4 cards):
- AI-generated questions
- Two-round adaptive assessment
- Performance analytics
- Personalised learning roadmap

### 9.3 QuizPage — Setup Screen
- Clean centred form, max-width `480px`
- "Start Your Assessment" heading
- Name input + Topic input with subtle icons
- Pill-style suggestions for popular topics below the topic field: `Python` `Machine Learning` `React` `System Design` `SQL` (clicking fills the input)
- "Generate Questions" CTA button (full width, accent)
- Inline validation: show error state on inputs if submitted empty

### 9.4 QuizPage — Quiz Screen (Round 1 & 2)
**Header bar:**
- Left: Round badge ("Round 1 — Foundations" / "Round 2 — Advanced")
- Centre: Progress indicator — `Question 3 / 5` with a segmented progress bar (5 segments, filled as answered)
- Right: Topic pill + Exit button

**Question cards:**
- One question visible at a time (not all stacked — implement prev/next navigation) OR all stacked with smooth scroll — **your choice, but one-at-a-time is preferred**
- Question number + text prominent
- MCQ options as large clickable cards (full row, not small radio buttons). Selected state: accent border + light accent background fill
- Answered questions show a small checkmark indicator in the progress bar

**Submit button:**
- Appears at bottom after all questions answered
- Shows count of unanswered questions if not all done: "Answer 2 more to submit"
- Disabled + tooltip if not all answered

**Loading state:**
- When generating questions: full skeleton screen with shimmer animation (3–5 placeholder cards)
- When submitting: overlay spinner with "Analysing your answers…" text

### 9.5 ResultsDashboard — Analytics Dashboard

This is the most important screen. Make it feel like a real analytics dashboard.

#### Score Header
- Student name + topic + round completed
- Two metric cards side-by-side (Round 2: show both R1 and R2 scores):
  - Circular progress ring (SVG, animated fill on mount) showing the score %
  - Below: "Proficiency Level" badge (Beginner / Intermediate / Advanced) with colour coding
- If Round 1 fail: show a warm encouraging message, NOT a harsh "disqualified" heading

#### Performance Breakdown (tabs or accordion)
Tab 1: **Overview**
- Strengths: list items with green checkmark icons and subtle green-tinted pill backgrounds
- Weak Areas: list items with amber warning icons and amber-tinted pill backgrounds
- If Round 2: a simple horizontal bar chart comparing R1 vs R2 score (pure CSS or SVG, no external chart library)

Tab 2: **Answer Review**
- All questions listed
- Each: question text, the 4 options shown as small pills, correct answer highlighted green, student's answer highlighted (green if correct, red if wrong)
- If Round 2: toggle to switch between Round 1 review and Round 2 review

Tab 3: **AI Analysis**
- Render the `generated_content.content` markdown string properly:
  - Parse `## Heading` → styled `<h2>`
  - Parse `### Heading` → styled `<h3>`
  - Parse `**bold**` → `<strong>`
  - Parse `- item` → styled list item with dot
  - Preserve paragraph breaks
- Give this section a slightly different background tint to stand out

Tab 4: **Learning Roadmap**
- Render `roadmap.content` same way as AI Analysis
- Show a visual timeline/stepper if the content has numbered steps (detect `1.`, `2.` etc.)

#### Footer action
- "Start New Assessment" button — prominent, full width on mobile

---

## 10. Specific Bugs to Fix While Redesigning

1. **Round 2 dedup bug** — `generateRound2Questions()` must send `round_1_questions` in the body (currently sends only `{ topic }`)
2. **Shared types** — extract all interfaces to `src/types.ts`, import in each component
3. **API URL** — use `const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'` instead of hardcoding
4. **Unanswered submission** — prevent form submit if any question has empty `student_answer`
5. **Toast placement** — ensure `<Toaster />` from `react-hot-toast` is rendered in `App.tsx` or `Layout.tsx`

---

## 11. Animation & Interaction Notes

- Score ring: SVG `stroke-dashoffset` animation on mount, 1s ease-out
- Question option select: scale(0.98) on press, border colour transition 150ms
- Tab switching: fade + slide (opacity + translateY, 200ms)
- Page transitions: fade between setup / quiz / results (optional but nice)
- Skeleton shimmer: CSS `@keyframes shimmer` with gradient sweep
- All hover states should have `transition: all 150ms ease`

---

## 12. What NOT to Do

- Do not use any external component library (no shadcn, no MUI, no Chakra) — pure Tailwind + custom CSS
- Do not use any chart library (recharts, chart.js etc.) — build score rings and bars in SVG/CSS
- Do not add new npm dependencies beyond what's already in `package.json`
- Do not change `App.tsx` routing structure
- Do not change any backend files
- Do not use `localStorage` or `sessionStorage`
- Do not use `Inter`, `Roboto`, or `Arial` as fonts
- Do not use purple/white gradient as the primary aesthetic (it's already overused)
- The `App.css` file has leftover Vite boilerplate styles — clear it or replace entirely

---

## 13. File Deliverables Expected

Replace/create these files:

```
src/types.ts                         ← NEW: shared TypeScript interfaces
src/index.css                        ← UPDATE: global styles, fonts, CSS variables
src/App.css                          ← UPDATE: clear boilerplate, add any global animations
src/App.tsx                          ← KEEP AS-IS (just add <Toaster /> if missing)
src/pages/HomePage.tsx               ← FULL REWRITE
src/pages/QuizPage.tsx               ← FULL REWRITE
src/components/Layout.tsx            ← FULL REWRITE
src/components/ResultsDashboard.tsx  ← FULL REWRITE
```

Optionally add:
```
src/components/ScoreRing.tsx         ← SVG score ring component
src/components/SkeletonLoader.tsx    ← shimmer skeleton
src/components/MarkdownRenderer.tsx  ← markdown-like string renderer
src/hooks/useQuiz.ts                 ← extract quiz logic from QuizPage if desired
```

---

## 14. Quick Smoke-Test Checklist

After completing the redesign, verify:

- [ ] Landing page loads at `/`
- [ ] "Start Learning" navigates to `/quiz`
- [ ] Name + topic validation shows inline errors
- [ ] Topic suggestion pills fill the input on click
- [ ] "Generate Questions" calls `POST /api/learning/generate-questions`
- [ ] Skeleton shows while questions load
- [ ] 5 MCQ questions render with clickable option cards
- [ ] Progress bar updates as questions are answered
- [ ] Submit is disabled until all 5 answered
- [ ] Round 1 submit calls `POST /api/learning/submit-round-1`
- [ ] Score < 50 → results dashboard shown immediately
- [ ] Score ≥ 50 → Round 2 questions generated (with `round_1_questions` in body)
- [ ] Round 2 submit calls `POST /api/learning/submit-round-2`
- [ ] Results dashboard shows score ring, tabs, answer review
- [ ] "Start New Assessment" resets all state
- [ ] Toast shows on API errors
- [ ] No TypeScript errors (`tsc --noEmit`)