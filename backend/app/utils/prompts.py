QUESTION_GENERATION_PROMPT = """
Generate 5 core concept Multiple Choice Questions (MCQ) about "{topic}".
Difficulty Level: {difficulty}

Return ONLY valid JSON array (no other text):

[
  {{"question": "...", "options": ["A", "B", "C", "D"], "correct_answer": "..."}}
]

Requirements for QUESTIONS:
- Generate Multiple Choice Questions with exactly 4 options each
- Difficulty Level: {difficulty} (beginner = basic concepts, intermediate = deeper understanding, advanced = complex scenarios)
- Options should be realistic but distinct
- One correct answer, three plausible distractors
- Each question should be clear and unambiguous

Requirements for OPTIONS:
- Always provide exactly 4 options
- Mix the correct answer position (don't always put it in the same spot)
- Make distractors realistic and related to the topic
- Format as a simple list of strings

Requirements for ANSWERS:
- Should be one of the 4 options provided
- Clear and factually correct
- Matches the difficulty level requested

OUTPUT FORMAT:
- Return ONLY valid JSON array
- No markdown, no code blocks, no explanations
- Each question must have "question", "options" (array of 4), and "correct_answer" fields
- No duplicate questions
"""

EVALUATION_PROMPT = """
Evaluate the learner answers.

Return ONLY valid JSON:

{{"score": 0, "strengths": [], "weak_areas": [], "level": ""}}

Topic: {topic}

Questions and Answers: {answers}

Requirements:

Strict JSON output
No markdown
No explanations outside JSON
"""

BEGINNER_EXPLANATION_PROMPT = """
Explain the topic for a beginner.

Include:

simple explanation
real-world examples
easy exercises
important concepts
Topic: {topic}

Weak Areas: {weak_areas}
"""

ADVANCED_CHALLENGES_PROMPT = """
Generate advanced challenge problems.

Include:

coding challenges
scenario-based problems
optimization questions
mini-project ideas
Topic: {topic}

Strengths: {strengths}
"""

ROADMAP_PROMPT = """
Generate a 30-day personalized learning roadmap.

Include:

daily study plan
revision schedule
project suggestions
practice exercises
improvement strategy
Weak Areas: {weak_areas}

Strengths: {strengths}

Level: {level}
"""
