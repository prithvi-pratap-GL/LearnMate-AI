QUESTION_GENERATION_PROMPT = """
Generate 5 UNIQUE, CORE CONCEPT Multiple Choice Questions (MCQ) specifically about "{topic}".
Difficulty Level: {difficulty}

Return ONLY valid JSON array (no other text):

[
  {{"question": "...", "options": ["A", "B", "C", "D"], "correct_answer": "..."}}
]

CRITICAL REQUIREMENTS:
1. Questions MUST BE UNIQUE - No repetition within this set
2. CORE CONCEPTS ONLY - Focus on fundamental/essential {topic} concepts, not edge cases
3. TO THE POINT - Direct questions testing knowledge, avoid lengthy narrative questions
4. TOPIC-SPECIFIC - Use {topic}-specific terminology and examples
5. DIFFICULTY LEVEL:
   - beginner: Basic definitions and fundamental concepts
   - intermediate: Deeper understanding, connections between concepts
   - advanced: Complex scenarios, problem-solving, implementation details

Requirements for QUESTIONS:
- Each question tests ONE specific {topic} concept
- Phrasing must be concise and clear
- Avoid ambiguity
- No generic or filler questions

Requirements for OPTIONS:
- Exactly 4 options per question
- Mix correct answer position (not always same spot)
- Plausible distractors related to {topic}, not obvious wrong answers
- All options must be realistic for the difficulty level

Requirements for ANSWERS:
- One of the 4 options provided
- Technically correct
- Matches the difficulty level requested

OUTPUT FORMAT:
- ONLY valid JSON array, no other text
- No markdown, no code blocks, no explanations
- Fields: "question", "options" (array of 4 strings), "correct_answer" (exact match of one option)
- NO DUPLICATE QUESTIONS within response
- NO GENERIC OR FILLER QUESTIONS
"""

EVALUATION_PROMPT = """
Act as an expert evaluator for the topic: {topic}.

First, reason step-by-step internally. For each question, compare the student's answer to the correct answer, assessing for correctness, depth, and clarity.
Based on your internal analysis, determine a score, strengths, weak areas, and a proficiency level.

Finally, format your complete evaluation as a single JSON object.
Return ONLY the valid JSON object below and nothing else.

Return ONLY valid JSON:

{{"score": 0, "strengths": [], "weak_areas": [], "level": ""}}

Topic: {topic}
Questions and Answers: {answers}

Requirements:
- Your entire output must be the JSON object.
- No markdown, no code blocks, no explanations outside the JSON.
"""

PERFORMANCE_ANALYSIS_PROMPT = """
Analyze the learner's performance in detail. Provide a pointwise breakdown of their answers.

TOPIC_IDENTIFIER: {topic}
Topic: {topic}
Score: {score}%

Questions and Answers:
{questions}

Generate a detailed performance analysis that includes:
1. Pointwise feedback on each question (what they got right/wrong and why)
2. Explanation of correct answers for questions they missed
3. Identification of their strengths based on correct answers
4. Specific areas to focus on for improvement
5. Positive reinforcement about their learning progress

Make the analysis specific to {topic} with relevant technical terminology and concepts.
"""

ADVANCED_CHALLENGES_PROMPT = """
Generate advanced challenge problems for {topic} at {level} level.

Topic: {topic}
Score: {score}%
Current Strengths: {strengths}

Include:
- Complex {topic} challenges specific to {topic} concepts
- Real-world scenario-based problems using {topic}
- Optimization and performance questions related to {topic}
- Mini-project ideas that demonstrate {topic} expertise
- Architecture and design patterns for {topic}

Make all challenges specific to {topic} with technical terminology and concrete examples.
"""

SOLUTION_EXPLANATION_PROMPT = """
Provide detailed explanations of the correct answers for the following questions in {topic}.

TOPIC_IDENTIFIER: {topic}
Topic: {topic}
Score: {score}%

Questions and Answers:
{questions}

Generate a detailed solution guide that includes:
1. For each question, explain why the correct answer is right
2. Provide the technical reasoning behind each correct answer
3. Explain common misconceptions students have
4. Include {topic}-specific concepts and terminology in explanations
5. Make explanations concise but thorough

Format as a clear, organized guide with explanations for each question.
"""

ROADMAP_PROMPT = """
Generate a personalized learning roadmap for {topic} at {level} level.

Topic: {topic}
Target Level: {level}
Current Score: {score}%
Strengths: {strengths}
Areas to Improve: {weak_areas}

Include:
- 30-day structured learning plan specific to {topic}
- Daily study schedule with {topic}-specific activities
- Milestones and checkpoints for {topic} mastery
- {topic}-specific projects and hands-on practice
- Technical concepts and terminology to master in {topic}
- Resources and best practices for {topic}
- Progress tracking strategy for {topic}

Make the roadmap highly specific to {topic} with concrete examples, technical terms, and {topic}-related project ideas.
"""

LLM_JUDGE_PROMPT = """
You are an educational evaluator.

Evaluate the student's answer fairly.

Question:
{question}

Correct Answer:
{correct_answer}

Student Answer:
{student_answer}

Return ONLY valid JSON:

{
  "correct": true,
  "score": 1,
  "reason": "short explanation"
}

Rules:

1. Be strict but fair
2. Accept conceptually correct answers
3. Reject unrelated or incorrect answers
4. score must be:

- 1 = correct
- 0 = incorrect

5. reason must be concise
6. No markdown
7. No extra text
8. Output ONLY JSON
"""