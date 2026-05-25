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
