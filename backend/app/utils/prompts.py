QUESTION_GENERATION_PROMPT = """
You MUST generate exactly 5 UNIQUE, CORE CONCEPT Multiple Choice Questions (MCQ) about "{topic}".
Difficulty Level: {difficulty}

===== CRITICAL OUTPUT FORMAT =====
Return ONLY valid JSON. Nothing else. No markdown, no code blocks, no explanation, no text before or after JSON.

[
  {{
    "question": "Complete question text here?",
    "options": ["First complete answer option text", "Second complete answer option text", "Third complete answer option text", "Fourth complete answer option text"],
    "correct_answer": "First complete answer option text"
  }},
  {{
    "question": "Another complete question text?",
    "options": ["Option A full text", "Option B full text", "Option C full text", "Option D full text"],
    "correct_answer": "Option B full text"
  }}
]

===== STRUCTURE VALIDATION =====
Every question MUST have exactly these 3 fields (no extra fields):
- "question": A clear question string ending with ?
- "options": An array with EXACTLY 4 strings (4 options, no more, no less)
- "correct_answer": Must be an EXACT substring match to one of the 4 options (case-sensitive)

===== OPTIONS FORMAT (CRITICAL) =====
Each option in the options array MUST be:
✓ A complete, standalone sentence or phrase (10+ characters minimum)
✓ Grammatically correct and readable
✓ NO letters like A), B), C), D), 1), 2) at start or anywhere
✓ NO brackets [ ] or parentheses ( ) around letters
✓ NO special characters or markdown formatting
✓ Just plain text describing the answer choice

WRONG format examples (DO NOT GENERATE):
- "A) This is wrong" ❌ Has letter prefix
- "[Option 1]" ❌ Has brackets
- "- First choice" ❌ Bullet formatting
- "1." ❌ Numbered format
- "**Bold text**" ❌ Markdown

CORRECT format examples (ONLY GENERATE THIS):
- "This describes a complete answer about the topic"
- "A method that implements inheritance patterns"
- "Synchronously handled data flow"
- "Asynchronously managed component lifecycle"

===== ANSWER MATCHING =====
The correct_answer field MUST be word-for-word identical to one of the 4 options.

Example:
"options": ["The first complete answer", "The second choice", "Wrong answer one", "Wrong answer two"]
"correct_answer": "The first complete answer"  ✓ EXACT MATCH

NEVER do this:
"correct_answer": "The first"  ❌ Partial match
"correct_answer": "the first complete answer"  ❌ Case mismatch

===== DIFFICULTY GUIDELINES =====
- beginner: Basic definitions, straightforward concepts, single-step reasoning
- intermediate: Practical application, connecting 2-3 ideas, common use cases
- advanced: Complex scenarios, edge cases, implementation details, troubleshooting

===== REQUIRED OUTPUT STEPS =====
1. Generate exactly 5 questions about {topic}
2. Ensure each question is unique and tests different concepts
3. Mix the position of correct answers (put correct answer in different positions across questions)
4. Verify each option is complete text (not letters or abbreviations)
5. Verify correct_answer exactly matches one option
6. Output ONLY the JSON array - nothing before or after
7. Validate JSON is properly formatted and parseable

===== FINAL VALIDATION BEFORE OUTPUT =====
Before returning, verify:
✓ Starts with [ and ends with ]
✓ Contains exactly 5 question objects
✓ Each question has exactly 3 fields: question, options, correct_answer
✓ Each options array has EXACTLY 4 string elements
✓ Each correct_answer is an exact match to one of the 4 options
✓ No question uses answer letters/numbers in option text
✓ No markdown, no code blocks, no explanations
✓ Valid JSON that can be parsed

Output ONLY the JSON array. Start with [ and end with ].
"""

EVALUATION_PROMPT = """
You are an expert evaluator for {topic}.

TASK: Evaluate the student's performance and return a JSON object with assessment data.

===== INPUT DATA =====
Topic: {topic}
Questions and Answers: {answers}

===== ANALYSIS TASK =====
For the given questions and student answers:
1. Evaluate each answer for correctness (compare to correct_answer)
2. Identify the student's strengths (topics/concepts they understand well)
3. Identify weak areas (topics/concepts needing improvement)
4. Determine overall proficiency level (beginner/intermediate/advanced)

===== REQUIRED OUTPUT FORMAT =====
You MUST output ONLY a valid JSON object. Nothing else. No explanation, no markdown, no code blocks.

Start immediately with {{ and end with }}.

Required JSON structure with EXACT field names:
{{
  "score": <number between 0-100>,
  "strengths": ["strength1", "strength2", "strength3"],
  "weak_areas": ["area1", "area2"],
  "level": "beginner|intermediate|advanced",
  "feedback": "2-3 sentence overall assessment"
}}

===== FIELD REQUIREMENTS =====

score: A percentage (0-100) representing overall performance
  - 0-40: Poor performance, needs foundational review
  - 40-60: Fair performance, has some gaps
  - 60-80: Good performance, minor gaps
  - 80-100: Excellent performance, well-understood

strengths: Array of 2-4 strings describing what the student did well
  Examples: ["Understands async/await patterns", "Strong grasp of state management"]
  - Each item should be a specific capability related to {topic}
  - Be specific, not generic

weak_areas: Array of 1-3 strings describing areas needing improvement
  Examples: ["Struggles with recursion", "Needs practice with error handling"]
  - Each item should be actionable
  - Be specific to {topic}

level: Must be EXACTLY one of: "beginner", "intermediate", "advanced"
  - beginner: Below 40% correct
  - intermediate: 40-75% correct
  - advanced: 75%+ correct

feedback: 2-3 sentences of encouragement or actionable guidance
  - Be constructive and motivating
  - Reference specific areas
  - End with an action item

===== OUTPUT RULES =====
✓ Return ONLY the JSON object
✓ Start with {{ and end with }}
✓ Use double quotes for all strings
✓ Arrays must use [ ] with comma-separated strings
✓ Strings must NOT contain unescaped quotes
✓ Valid JSON that can be parsed

ABSOLUTELY NO:
❌ Text before the JSON
❌ Code blocks or markdown
❌ Explanation after the JSON
❌ Multiple JSON objects
❌ Incomplete JSON (all 5 fields required)

===== EXAMPLE CORRECT OUTPUT =====
{{
  "score": 75,
  "strengths": ["Correctly identifies class syntax", "Understands inheritance", "Good error handling practices"],
  "weak_areas": ["Struggles with polymorphism", "Needs practice with abstract classes"],
  "level": "intermediate",
  "feedback": "You're making solid progress with OOP fundamentals. Focus on polymorphism concepts this week - they'll strengthen your understanding of inheritance patterns you've already mastered."
}}

===== STRICT VALIDATION =====
Before returning, verify:
✓ Starts with {{ and ends with }}
✓ Contains exactly 5 fields: score, strengths, weak_areas, level, feedback
✓ score is a number 0-100
✓ strengths is an array of 2-4 strings
✓ weak_areas is an array of 1-3 strings
✓ level is exactly "beginner", "intermediate", or "advanced"
✓ feedback is a string of 2-3 sentences
✓ Valid parseable JSON

Output ONLY the JSON object. No preamble, no explanation. Start with {{ immediately.
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
You are an expert educational evaluator. Your task is to evaluate if a student's answer is correct.

===== EVALUATION INPUT =====
Question: {question}
Correct Answer: {correct_answer}
Student Answer: {student_answer}

===== EVALUATION CRITERIA =====
- Be fair but accurate
- Accept answers that are conceptually correct or semantically equivalent
- Reject answers that are unrelated, incorrect, or incomplete
- Consider minor phrasing differences if the core concept is correct

===== REQUIRED JSON OUTPUT =====
You MUST output ONLY a valid JSON object. Nothing else. No explanation, no text before or after.

Start immediately with {{ and end with }}.

Required structure (EXACTLY 3 fields):
{{
  "correct": true,
  "score": 1,
  "reason": "Brief 1-2 sentence explanation of why this answer is correct/incorrect"
}}

===== FIELD REQUIREMENTS =====

correct: Boolean (true or false)
  - true: Student answer is correct or conceptually equivalent
  - false: Student answer is incorrect or unrelated

score: Integer (must be 1 or 0 only)
  - 1: Correct answer
  - 0: Incorrect answer

reason: String (1-2 sentences max)
  - Briefly explain your judgment
  - Examples:
    - "Correct: Accurately describes the concept"
    - "Incorrect: Misses the key aspect of X"
    - "Correct: Equivalent phrasing of the concept"
  - Must be concise (no long explanations)

===== OUTPUT VALIDATION =====
✓ Starts with {{ and ends with }}
✓ All field names in double quotes
✓ correct is boolean (true or false, no quotes)
✓ score is 1 or 0 (number, no quotes)
✓ reason is a string (in double quotes)
✓ Valid parseable JSON

ABSOLUTELY NO:
❌ Text before the JSON
❌ Text after the JSON
❌ Markdown, code blocks, or formatting
❌ Extra fields beyond the 3 required
❌ Multiple JSON objects
❌ Incomplete JSON (all 3 fields required)

===== EXAMPLE CORRECT OUTPUTS =====

Example 1:
{{
  "correct": true,
  "score": 1,
  "reason": "Correct: The student's answer accurately describes the concept of inheritance in OOP."
}}

Example 2:
{{
  "correct": false,
  "score": 0,
  "reason": "Incorrect: The answer confuses inheritance with composition, which are different concepts."
}}

Example 3:
{{
  "correct": true,
  "score": 1,
  "reason": "Correct: While phrased differently, the student's answer captures the essential meaning."
}}

===== STRICT VALIDATION =====
Before returning, verify:
✓ Output is exactly 3 JSON fields: correct, score, reason
✓ correct is true or false (boolean)
✓ score is 1 or 0 (integer)
✓ reason is a non-empty string (2-15 words)
✓ Proper JSON formatting
✓ No text before {{ or after }}

Output ONLY the JSON object. Start with {{ immediately. Do not include any explanation.
"""