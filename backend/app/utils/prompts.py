QUESTION_GENERATION_PROMPT = """
You MUST generate exactly 5 UNIQUE, CORE CONCEPT Multiple Choice Questions (MCQ) about "{topic}".
Difficulty Level: {difficulty}

===== CRITICAL OUTPUT FORMAT =====
Return ONLY valid JSON array. Nothing else. No markdown, no code blocks, no explanation, no text before or after.

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
Every question MUST have exactly these 3 fields (no extra fields, no rearranging):
- "question": A clear question string ending with ?
  * Must be 20-150 characters
  * Must end with ? (question mark)
  * Must be grammatically correct
  * NO markdown, NO special formatting

- "options": An array with EXACTLY 4 strings (no more, no less)
  * Must have 4 elements exactly
  * Each element is a complete answer option
  * Must be different from each other
  * One must match correct_answer exactly

- "correct_answer": Must be an EXACT word-for-word match to one of the 4 options
  * Must be case-sensitive match
  * Must be complete text, not partial
  * No variations, no abbreviations

===== OPTIONS FORMAT (CRITICAL) =====
Each option in the options array MUST be:
✓ A complete, standalone sentence or phrase (15-80 characters minimum)
✓ Grammatically correct and readable English
✓ NO letters like A), B), C), D), 1), 2) anywhere in text
✓ NO brackets [ ] or parentheses ( ) anywhere
✓ NO bullet points or dashes at start
✓ NO special characters unless part of normal text (hyphen in word is ok)
✓ NO markdown formatting (NO **, NO ##, NO --, etc)
✓ NO code syntax (NO backticks, NO brackets)
✓ Just plain text describing the answer choice
✓ All options must be unique (no duplicates)

WRONG format examples (DO NOT GENERATE THESE):
- "A) This is wrong" ❌ Letter prefix
- "B. Multiple choice" ❌ Letter + period
- "[Option 1]" ❌ Brackets around text
- "- First choice" ❌ Dash at start
- "1. The answer" ❌ Number at start
- "**Bold text**" ❌ Markdown bold
- "Option_1" ❌ Underscore
- "Option|Choice" ❌ Pipe character
- "(a) text" ❌ Parenthesized letter
- "```code```" ❌ Code blocks

CORRECT format examples (ONLY GENERATE THIS):
- "This describes a complete answer about the topic"
- "A method that implements inheritance patterns"
- "Synchronously handled data flow in components"
- "Asynchronously managed component lifecycle"
- "Handling errors with try-catch blocks"
- "Using const instead of var for variables"

===== ANSWER MATCHING (EXACT WORD-FOR-WORD) =====
The correct_answer field MUST be 100% identical to one of the 4 options.

Correct examples:
"options": ["The first complete answer", "The second choice", "Wrong answer one", "Wrong answer two"]
"correct_answer": "The first complete answer"  ✓ EXACT MATCH (matches exactly)

NEVER do this (will fail):
"correct_answer": "The first"  ❌ PARTIAL match
"correct_answer": "the first complete answer"  ❌ CASE mismatch (lowercase vs uppercase)
"correct_answer": "The first complete answer "  ❌ Extra space
"correct_answer": "First complete answer, The"  ❌ Different order
"correct_answer": "The first complete answers"  ❌ Plural mismatch

===== DIFFICULTY GUIDELINES =====
{difficulty} difficulty level:
- beginner: Basic definitions, straightforward concepts, single-step reasoning, fundamental knowledge
- intermediate: Practical application, connecting 2-3 ideas, common use cases, applied knowledge
- advanced: Complex scenarios, edge cases, implementation details, troubleshooting, expert knowledge

===== REQUIRED GENERATION STEPS =====
1. Generate exactly 5 unique questions about {topic}
2. Test different core concepts (not the same concept 5 times)
3. Ensure {difficulty} difficulty level for all questions
4. Mix the position of correct answers (Q1 correct=option[0], Q2 correct=option[2], Q3 correct=option[3], etc)
5. Verify each option is plain text (not letters, brackets, bullets)
6. Verify correct_answer matches an option exactly (case-sensitive, full text)
7. Output ONLY the JSON array - nothing before or after
8. Validate JSON is properly formatted and parseable

===== EDGE CASE HANDLING =====
- If topic is vague: generate questions testing core concepts of the field
- If difficulty is unclear: generate intermediate-level questions
- Always generate all 5 questions even if topic is unusual
- Never skip a question, never generate fewer than 5

===== FINAL VALIDATION BEFORE OUTPUT =====
Before returning, verify EVERY point:
✓ Starts with [ exactly
✓ Ends with ] exactly
✓ Contains exactly 5 question objects (no more, no less)
✓ Each question has exactly 3 fields: question, options, correct_answer
✓ Each options array has EXACTLY 4 string elements
✓ Each option is 15-80 characters (plain text, no formatting)
✓ Each correct_answer is EXACT match (word-for-word, case-sensitive) to one of 4 options
✓ All options in a question are unique (no duplicates)
✓ No question text is under 20 characters
✓ No markdown, no code blocks, no explanations before/after JSON
✓ No letters/numbers/brackets in option text
✓ Valid JSON that can be parsed with json.loads()
✓ Test: Can I json.loads() this output? (must be yes)

If any check fails, regenerate questions until all pass.

Output ONLY the JSON array. Start with [ exactly and end with ] exactly. No text before or after.
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

===== EDGE CASE HANDLING =====
If input is incomplete or malformed:
- If no answers provided: output score=0, level="beginner", generic feedback
- If topic is unclear: evaluate based on available answer content
- If question data is missing: evaluate answers against general knowledge
- Never skip any field - all 5 fields are REQUIRED

===== REQUIRED OUTPUT FORMAT =====
You MUST output ONLY a valid JSON object. Nothing else. No explanation, no markdown, no code blocks.

Start immediately with {{ and end with }}.

Required JSON structure with EXACT field names (NO extra fields, NO rearranging):
{{
  "score": <number between 0-100>,
  "strengths": [<string>, <string>],
  "weak_areas": [<string>],
  "level": "<beginner|intermediate|advanced>",
  "feedback": "<string>"
}}

===== FIELD REQUIREMENTS =====

score: An INTEGER percentage (0-100) representing overall performance
  - Must be a whole number (0, 25, 50, 75, 100, etc.)
  - 0-40: Poor performance, needs foundational review
  - 40-60: Fair performance, has some gaps
  - 60-80: Good performance, minor gaps
  - 80-100: Excellent performance, well-understood
  - ALWAYS calculate: (correct_count / total_questions * 100) rounded to nearest integer

strengths: Array of 2-4 strings describing what the student did well
  - Minimum 2 items, maximum 4 items
  - Examples: ["Understands async/await patterns", "Strong grasp of state management", "Excellent error handling", "Good debugging skills"]
  - Each item must be specific capability related to {topic}
  - Each string must be 10-60 characters
  - NO bullets, NO dashes, NO numbers at start
  - Plain text only

weak_areas: Array of 1-3 strings describing areas needing improvement
  - Minimum 1 item, maximum 3 items
  - Examples: ["Struggles with recursion", "Needs practice with error handling", "Weak on edge cases"]
  - Each item must be actionable and specific to {topic}
  - Each string must be 10-60 characters
  - NO bullets, NO dashes, NO numbers at start
  - Plain text only

level: Must be EXACTLY one of these strings (lowercase, no quotes in output): "beginner", "intermediate", "advanced"
  - Compare to score: beginner if score<40, intermediate if 40-75, advanced if 75+
  - This must match the score level
  - NO variations: not "Beginner", not "BEGINNER", not "novice"

feedback: String of 2-3 sentences (50-200 characters total)
  - First sentence: constructive assessment
  - Second sentence: reference specific areas from strengths or weak_areas
  - Third sentence (optional): actionable next step
  - Be encouraging and motivating
  - NO bullet points, NO numbers, NO extra formatting

===== OUTPUT RULES =====
✓ Return ONLY the JSON object (5 fields exactly)
✓ Start with {{ (double brace) and end with }} (double brace)
✓ Use double quotes ONLY around string values
✓ Arrays use [ ] with comma-separated strings in double quotes
✓ Numbers (score) have NO quotes
✓ Booleans: n/a
✓ All special characters in strings must be properly escaped
✓ No newlines or tabs inside string values
✓ Valid JSON that can be parsed with json.loads()

ABSOLUTELY NO (will fail):
❌ Text before the first {{
❌ Text after the last }}
❌ Code blocks (```) or markdown
❌ Single quotes (use double quotes only)
❌ Unescaped special characters in strings
❌ Extra fields (only 5 allowed)
❌ Missing fields (all 5 required)
❌ Arrays with wrong count (strengths 2-4, weak_areas 1-3)
❌ level as anything other than beginner/intermediate/advanced

===== EXAMPLE CORRECT OUTPUTS =====

Example 1 (Advanced):
{{
  "score": 85,
  "strengths": ["Correctly identifies class syntax", "Understands inheritance patterns", "Good error handling practices"],
  "weak_areas": ["Needs practice with abstract classes"],
  "level": "advanced",
  "feedback": "Excellent understanding of OOP fundamentals. Your mastery of inheritance and error handling shows strong progress. Focus on abstract classes and polymorphism to reach expert level."
}}

Example 2 (Intermediate):
{{
  "score": 60,
  "strengths": ["Grasps basic function concepts", "Understands variable scope"],
  "weak_areas": ["Struggles with closures", "Weak on async patterns"],
  "level": "intermediate",
  "feedback": "You have a solid foundation in functions and scope. Practice closures this week to strengthen your understanding. Building closure skills will make async patterns easier to learn next."
}}

Example 3 (Beginner):
{{
  "score": 30,
  "strengths": ["Recognizes syntax structure", "Familiar with basic operations"],
  "weak_areas": ["Limited understanding of core concepts", "Needs practice with control flow"],
  "level": "beginner",
  "feedback": "You're starting your learning journey. Review core concepts of {topic} before advancing. Practice daily with simple examples to build a strong foundation."
}}

===== STRICT VALIDATION BEFORE OUTPUT =====
Before returning JSON, verify EVERY point:
✓ Exactly {{ at start, exactly }} at end
✓ Exactly 5 fields: score, strengths, weak_areas, level, feedback
✓ score is 0-100 integer (no decimal point, no quotes)
✓ strengths is array with 2-4 string items
✓ weak_areas is array with 1-3 string items
✓ level is exactly one of: "beginner", "intermediate", "advanced"
✓ feedback is non-empty string (50-200 chars)
✓ No text before {{ or after }}
✓ Valid JSON (test parseable with json.loads)
✓ All strings use double quotes, no single quotes
✓ No unescaped special characters
✓ Score level matches proficiency level

If ANY check fails, reconstruct the entire JSON correctly.

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
- If student answer is empty/null/missing: score 0 as incorrect
- If inputs are malformed: evaluate based on available content

===== EDGE CASE HANDLING =====
1. Empty student answer: Always output score=0, correct=false, reason="No answer provided"
2. Unclear question: Evaluate answer against common sense interpretation
3. Ambiguous correct_answer: Give benefit of doubt if answer shows correct understanding
4. Student answer partially correct: If captures main concept, score 1; if incomplete, score 0
5. Typos/grammar errors: Ignore minor spelling, evaluate concept accuracy only
6. Similar but different phrasing: If conveys same meaning, score 1

===== REQUIRED JSON OUTPUT =====
You MUST output ONLY a valid JSON object. Nothing else. No explanation, no text before or after.

Start immediately with {{ and end with }}.

Required structure (EXACTLY 3 fields, NO MORE, NO LESS):
{{
  "correct": <true or false>,
  "score": <1 or 0>,
  "reason": "<string>"
}}

===== FIELD REQUIREMENTS =====

correct: Boolean (exactly true or false, lowercase, NO quotes)
  - true: Student answer is correct or conceptually equivalent
  - false: Student answer is incorrect, incomplete, or unrelated
  - If score=1 then correct MUST be true
  - If score=0 then correct MUST be false
  - MUST align with score value

score: Integer (EXACTLY 1 or 0, NO decimals, NO quotes)
  - 1: Correct answer (full credit)
  - 0: Incorrect answer (no credit)
  - NO 0.5, NO 2, only 0 or 1
  - If student answer is empty: score=0
  - score value MUST match correct boolean

reason: String (1-2 sentences, 20-100 characters)
  - Concise explanation of judgment
  - Start with "Correct:" or "Incorrect:"
  - Examples (MUST follow this format):
    - "Correct: Accurately describes the inheritance concept."
    - "Incorrect: Confuses inheritance with composition."
    - "Correct: Equivalent phrasing of the right answer."
    - "Incorrect: Missing key aspect of the concept."
  - Be specific about why or why not
  - NO lists, NO bullets, NO numbers
  - NO markdown, NO special formatting

===== OUTPUT RULES (CRITICAL) =====
✓ Starts with {{ (double open brace) and ends with }} (double close brace)
✓ Exactly 3 fields: correct, score, reason
✓ Field names in double quotes: "correct", "score", "reason"
✓ Commas between fields: "correct": <value>, "score": <value>, "reason": "<value>"
✓ correct value is boolean (true or false, NO quotes, lowercase)
✓ score value is integer 0 or 1 (NO quotes, NO decimals)
✓ reason value is string (IN double quotes)
✓ All strings use double quotes only (NO single quotes)
✓ No newlines or tabs inside strings
✓ Valid JSON parseable with json.loads()

ABSOLUTELY NO (will fail):
❌ Text before the first {{
❌ Text after the last }}
❌ Markdown code blocks (```)
❌ Single quotes for strings
❌ Unescaped characters in strings (use \\")
❌ Extra fields beyond 3
❌ Missing fields (all 3 required)
❌ Incomplete/truncated JSON
❌ Multiple JSON objects
❌ Booleans with quotes: "true" or "false"
❌ score as decimal: 0.5, 1.0
❌ Mismatch: score=1 but correct=false
❌ reason longer than 100 characters

===== CORRECT JSON FORMAT EXAMPLES =====

Example 1 (Student correct):
{{
  "correct": true,
  "score": 1,
  "reason": "Correct: Accurately describes inheritance and polymorphism concepts."
}}

Example 2 (Student incorrect):
{{
  "correct": false,
  "score": 0,
  "reason": "Incorrect: Confuses inheritance with composition patterns."
}}

Example 3 (Correct but different wording):
{{
  "correct": true,
  "score": 1,
  "reason": "Correct: Different wording but captures the essential concept."
}}

Example 4 (Empty answer):
{{
  "correct": false,
  "score": 0,
  "reason": "Incorrect: No answer was provided."
}}

Example 5 (Partially correct):
{{
  "correct": false,
  "score": 0,
  "reason": "Incorrect: Grasps part of concept but misses key aspect."
}}

===== BEFORE OUTPUT, VERIFY EVERY POINT =====
Validation checklist:
✓ Exactly {{ at position 0, exactly }} at end
✓ Exactly 3 fields in order: correct, score, reason
✓ correct value is true or false (boolean, lowercase, no quotes)
✓ score value is 0 or 1 (integer, no quotes, no decimals)
✓ reason is non-empty string in double quotes (20-100 chars)
✓ correct boolean matches score: (score=1 → correct=true), (score=0 → correct=false)
✓ reason starts with "Correct:" or "Incorrect:"
✓ No text outside {{ and }}
✓ No markdown, no code blocks, no formatting
✓ All strings use double quotes, no single quotes
✓ Valid JSON: can be parsed as json.loads(output)
✓ No special characters unless properly escaped

If any check fails, reconstruct the entire JSON correctly before outputting.

Output ONLY the JSON object. No preamble, no explanation. Start with {{ immediately.
"""