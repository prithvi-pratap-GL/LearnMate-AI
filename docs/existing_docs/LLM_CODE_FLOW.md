# LearnMate AI - LLM Code Flow Deep Dive

## File Structure

```
backend/app/
├── routes/
│   └── learning.py                    # API endpoints that orchestrate the workflow
├── services/
│   ├── question_service.py            # Generates MCQ questions
│   ├── evaluation_service.py          # Evaluates student answers (judge)
│   ├── challenge_service.py           # Generates performance analysis, solutions, challenges
│   ├── roadmap_service.py             # Generates personalized learning roadmaps
│   └── huggingface_service.py         # Low-level LLM API calls and mock responses
├── utils/
│   └── prompts.py                     # All prompt templates used
└── config/
    └── settings.py                    # Configuration (API keys, etc.)
```

---

## Flow 1: Question Generation

### Code Chain

```
frontend
    ↓
learning.py: POST /generate-questions
    ↓
    body = {"topic": "Python Programming"}
    ↓
    questions = await question_service.generate_questions(topic, difficulty="beginner")
    ↓
question_service.py:
    ├─ prompt = QUESTION_GENERATION_PROMPT.format(topic="Python Programming", difficulty="beginner")
    │
    ├─ response = await query_model(prompt)
    │
    └─ return JSON parsed questions
    ↓
huggingface_service.py:
    ├─ query_model(prompt, model="mistralai/Mistral-7B-Instruct-v0.2")
    │
    ├─ Creates HTTP POST to Hugging Face:
    │  POST https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2
    │  Headers: Authorization: Bearer {HUGGING_FACE_API_KEY}
    │  Body: {"inputs": prompt}
    │
    ├─ Response: [{"generated_text": "[{\"question\": \"...\", \"options\": [...], ...}]"}]
    │
    └─ Parse and return questions
    ↓
frontend
    Response: {"questions": [...], "round": 1, "total_questions": 5}
```

### Code Example

**learning.py (Route Handler)**
```python
@router.post("/generate-questions")
async def generate_questions(http_request: Request):
    body = json.loads(await http_request.body())
    topic = body.get("topic", "General")
    
    # Call question service
    questions = await question_service.generate_questions(topic, difficulty="beginner")
    questions = questions[:ROUND_1_QUESTION_COUNT]  # Limit to 5
    
    return {"questions": questions, "round": 1, "total_questions": len(questions)}
```

**question_service.py (Service Logic)**
```python
async def generate_questions(topic: str, num_questions: int = 5, difficulty: str = "beginner"):
    # Format prompt with topic and difficulty
    prompt = QUESTION_GENERATION_PROMPT.format(topic=topic, difficulty=difficulty)
    
    try:
        # Send to LLM
        response = await query_model(prompt)
        
        # Parse response
        if isinstance(response, list) and len(response) > 0:
            generated_text = response[0].get('generated_text', '[]')
            
            # Extract JSON from response
            json_str_start = generated_text.find('[')
            json_str_end = generated_text.rfind(']') + 1
            
            if json_str_start != -1 and json_str_end > json_str_start:
                json_str = generated_text[json_str_start:json_str_end]
                questions_data = json.loads(json_str)
                return questions_data
    except Exception as e:
        raise ValueError(f"Failed to generate questions: {e}")
```

**huggingface_service.py (API Call)**
```python
async def query_model(prompt: str, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
    session_timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=session_timeout) as session:
        payload = {"inputs": prompt}
        try:
            # Make API call to Hugging Face
            async with session.post(
                API_URL + model,
                headers={"Authorization": f"Bearer {settings.HUGGING_FACE_API_KEY}"},
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            print(f"[WARNING] API error: {e}")
            # Fallback to mock response
            return generate_mock_response(prompt)
```

**prompts.py (Template)**
```python
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
- CRITICAL: Ensure questions are UNIQUE and NOT REPEATED across different difficulty levels

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
- No duplicate questions within the response
- No questions that repeat content from other difficulty levels
"""
```

---

## Flow 2: Answer Submission & Evaluation

### Code Chain

```
frontend
    ↓
learning.py: POST /submit-round-1
    ↓
    request = {
        "student_name": "Alice",
        "topic": "Python Programming",
        "questions": [
            {"question": "What is...", "student_answer": "pip", "correct_answer": "pip"},
            ...
        ]
    }
    ↓
evaluation_service.evaluate_learning(request)
    ↓
evaluation_service.py:
    ├─ Calculate score: int((3/5) * 100) = 60
    │
    ├─ Create evaluation prompt with answers
    │
    ├─ response = await query_model(prompt, model="meta-llama/Llama-2-70b-chat-hf")
    │
    └─ Parse and return evaluation JSON
    ↓
huggingface_service.py:
    ├─ query_model(prompt, model="meta-llama/Llama-2-70b-chat-hf")
    │
    ├─ Llama 70B analyzes:
    │  - Which answers were correct/incorrect
    │  - Depth of understanding
    │  - Key strengths
    │  - Areas needing improvement
    │  - Appropriate proficiency level
    │
    └─ Returns evaluation JSON
    ↓
learning.py:
    ├─ If score < 50%:
    │  ├─ Generate performance analysis
    │  └─ Return: {"status": "completed", "evaluation": {...}, "generated_content": {...}}
    │
    └─ If score >= 50%:
       └─ Return: {"status": "proceed_to_round_2", "score": 60, "evaluation": {...}}
    ↓
frontend
    ├─ Show score and evaluation
    ├─ If score < 50%: Show performance analysis + END
    └─ If score >= 50%: Proceed to Round 2
```

### Code Example

**learning.py (Route Handler)**
```python
@router.post("/submit-round-1")
async def submit_round_1(request: Round1SubmissionRequest):
    # Convert request data
    questions_list = [
        QuestionAnswer(**q) if isinstance(q, dict) else q
        for q in request.questions
    ]
    analysis_request = LearningAnalysisRequest(
        student_name=request.student_name,
        topic=request.topic,
        questions=questions_list
    )

    # Evaluate using specialized judge model
    evaluation = await evaluation_service.evaluate_learning(analysis_request)
    score = evaluation.get("score", 0)
    strengths = evaluation.get("strengths", [])
    weak_areas = evaluation.get("weak_areas", [])
    level = evaluation.get("level", "Beginner")

    # Generate roadmap
    roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas, score, request.topic)
    roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

    if score < 50:
        # Low score: Show performance analysis
        questions_dict = [q.model_dump() if hasattr(q, 'model_dump') else q for q in questions_list]
        content = await challenge_service.generate_performance_analysis(request.topic, questions_dict, score)
        generated_content = {"type": "performance_analysis", "content": content}

        return {
            "status": "completed",
            "round": 1,
            "evaluation": evaluation,
            "generated_content": generated_content,
            "roadmap": roadmap,
            "can_proceed_to_round_2": False
        }
    else:
        # High score: Proceed to Round 2
        return {
            "status": "proceed_to_round_2",
            "round": 1,
            "score": score,
            "evaluation": evaluation,
            "can_proceed_to_round_2": True
        }
```

**evaluation_service.py (Evaluation Logic)**
```python
# Model options for evaluation (ordered by preference)
EVALUATION_MODELS = [
    "meta-llama/Llama-2-70b-chat-hf",  # Primary
    "mistralai/Mistral-Large-Instruct-2407",
    "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
    "mistralai/Mistral-7B-Instruct-v0.2",  # Fallback
]

async def evaluate_learning(request: LearningAnalysisRequest, model_index: int = 0):
    # Step 1: Calculate score by comparing answers
    questions_list = [
        {
            "question": q.question,
            "student_answer": q.student_answer,
            "correct_answer": q.correct_answer
        }
        for q in request.questions
    ]

    score = calculate_score_from_answers(questions_list)
    
    # Step 2: Create evaluation prompt
    answers_json = json.dumps(questions_list)
    answers_str = f"Score: {score}\n\n" + answers_json
    
    prompt = EVALUATION_PROMPT.format(topic=request.topic, answers=answers_str)

    try:
        # Step 3: Send to specialized evaluation model (Llama 70B)
        selected_model = EVALUATION_MODELS[model_index]
        response = await query_model(prompt, model=selected_model)

        # Step 4: Parse response
        if isinstance(response, list) and len(response) > 0:
            generated_text = response[0].get('generated_text', '{}')
            
            # Extract JSON object
            json_str_start = generated_text.rfind('{')
            json_str_end = generated_text.rfind('}') + 1
            
            if json_str_start != -1 and json_str_end > json_str_start:
                json_str = generated_text[json_str_start:json_str_end]
                evaluation_data = json.loads(json_str)
                evaluation_data['score'] = score  # Use calculated score
                return evaluation_data
    except Exception as e:
        raise e
```

**prompts.py (Evaluation Template)**
```python
EVALUATION_PROMPT = """
Act as an expert evaluator for the topic: {topic}.

First, reason step-by-step internally. For each question, compare the student's answer to the correct answer, 
assessing for correctness, depth, and clarity.

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
```

---

## Flow 3: Round 2 Question Generation (with Filtering)

### Code Chain

```
frontend
    ↓
learning.py: POST /generate-round-2-questions
    ↓
    request = {
        "topic": "Python Programming",
        "round_1_questions": [Q1, Q2, Q3, Q4, Q5]  # ← IMPORTANT: Pass Round 1 questions
    }
    ↓
question_service.generate_questions(topic, difficulty="advanced")
    ↓
    questions = Generate 5+ advanced questions (more than needed)
    ↓
    Filter: Remove any questions matching Round 1
    │
    ├─ round_1_q_texts = {q.get("question").lower() for q in round_1_questions}
    ├─ filtered_questions = [q for q in questions if q.get("question").lower() not in round_1_q_texts]
    │
    └─ If less than 5 remain, generate more until we have 5 unique questions
    ↓
return filtered_questions[:5]
    ↓
frontend
    Response: {"questions": [...], "round": 2, "total_questions": 5}
```

### Code Example

**learning.py (Route Handler - Updated)**
```python
@router.post("/generate-round-2-questions")
async def generate_round_2_questions(http_request: Request):
    """Generate advanced challenge questions for Round 2, excluding Round 1 questions"""
    try:
        body = json.loads(await http_request.body())
        topic = body.get("topic", "General")
        round_1_questions = body.get("round_1_questions", [])  # ← Get Round 1 questions

        # Generate more advanced questions
        questions = await question_service.generate_questions(topic, difficulty="advanced")

        # FILTER: Remove questions that were in Round 1
        round_1_q_texts = {q.get("question", "").lower() for q in round_1_questions}
        filtered_questions = [
            q for q in questions
            if q.get("question", "").lower() not in round_1_q_texts
        ]

        # If we filtered out too many, generate more to reach at least 5
        if len(filtered_questions) < 5:
            all_questions = filtered_questions
            attempts = 0
            while len(all_questions) < 5 and attempts < 3:
                more_questions = await question_service.generate_questions(topic, difficulty="advanced")
                for q in more_questions:
                    if q.get("question", "").lower() not in round_1_q_texts and q not in all_questions:
                        all_questions.append(q)
                        if len(all_questions) >= 5:
                            break
                attempts += 1
            filtered_questions = all_questions[:5]

        return {"questions": filtered_questions[:5], "round": 2, "total_questions": len(filtered_questions[:5])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Flow 4: Round 2 Submission & Final Report

### Code Chain

```
frontend
    ↓
learning.py: POST /submit-round-2
    ↓
    request = {
        "student_name": "Alice",
        "topic": "Python Programming",
        "questions": [...advanced answers...],
        "round_1_score": 60,
        "round_1_evaluation": {...}
    }
    ↓
[1] Evaluate Round 2 (same as Round 1, but with advanced questions)
    └─ evaluation = await evaluation_service.evaluate_learning(analysis_request)
    ↓
[2] Generate Solution Explanations
    └─ content = await challenge_service.generate_solution_explanation(topic, questions, score)
    ↓
[3] Generate Personalized Roadmap
    └─ roadmap = await roadmap_service.generate_roadmap(level, strengths, weak_areas, score, topic)
    ↓
[4] Optional: Generate Advanced Challenges
    └─ challenges = await challenge_service.generate_advanced_challenges(topic, strengths, score, level)
    ↓
return {
    "status": "completed",
    "round": 2,
    "round_1_score": 60,
    "round_2_evaluation": {...},
    "generated_content": {...solutions...},
    "roadmap": {...personalized roadmap...},
    "questions": [...]
}
    ↓
frontend
    Show comprehensive report with:
    ✓ Both Round 1 & 2 scores
    ✓ Strengths and weaknesses
    ✓ Solution explanations
    ✓ 30-day learning roadmap
```

### Code Example

**learning.py (Round 2 Handler)**
```python
@router.post("/submit-round-2")
async def submit_round_2(request: Round2SubmissionRequest):
    """Submit Round 2 answers and provide detailed analysis with roadmap."""
    try:
        # Convert request data
        questions_list = [
            QuestionAnswer(**q) if isinstance(q, dict) else q
            for q in request.questions
        ]
        analysis_request = LearningAnalysisRequest(
            student_name=request.student_name,
            topic=request.topic,
            questions=questions_list
        )

        # [1] Evaluate Round 2
        evaluation = await evaluation_service.evaluate_learning(analysis_request)
        score = evaluation.get("score", 0)
        strengths = evaluation.get("strengths", [])
        weak_areas = evaluation.get("weak_areas", [])
        level = evaluation.get("level", "Advanced")

        # [2] Generate solution explanations
        questions_dict = [q.model_dump() if hasattr(q, 'model_dump') else q for q in questions_list]
        content = await challenge_service.generate_solution_explanation(request.topic, questions_dict, score)
        generated_content = {"type": "solution", "content": content}

        # [3] Generate personalized roadmap
        roadmap_content = await roadmap_service.generate_roadmap(level, strengths, weak_areas, score, request.topic)
        roadmap = {"title": f"Personalized Roadmap for {level}", "content": roadmap_content}

        # [4] Return comprehensive report
        return {
            "status": "completed",
            "round": 2,
            "round_1_score": request.round_1_score,
            "round_2_evaluation": evaluation,
            "generated_content": generated_content,
            "roadmap": roadmap,
            "questions": questions_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**roadmap_service.py (Roadmap Generation)**
```python
async def generate_roadmap(level: str, strengths: list, weak_areas: list, score: int = 50, topic: str = ""):
    """
    Generates a personalized learning roadmap at one level higher than current level.
    Beginner → Intermediate, Intermediate → Advanced, Advanced → Expert
    """
    # Determine target level (one step higher)
    level_hierarchy = {
        "Beginner": "Intermediate",
        "Intermediate": "Advanced",
        "Advanced": "Expert"
    }
    target_level = level_hierarchy.get(level, "Advanced")

    # Create prompt with all context
    prompt = ROADMAP_PROMPT.format(
        topic=topic,
        level=target_level,
        strengths=", ".join(strengths),
        weak_areas=", ".join(weak_areas),
        score=score
    )
    
    try:
        # Generate roadmap
        response = await query_model(prompt)
        if isinstance(response, list) and len(response) > 0:
            return response[0].get('generated_text', '')
        return ''
    except Exception as e:
        raise Exception(f"Failed to generate roadmap: {e}")
```

**challenge_service.py (Solution Explanations)**
```python
async def generate_solution_explanation(topic: str, questions: list, score: int = 75):
    """
    Generates detailed explanations of correct answers for the given questions.
    """
    questions_json = json.dumps(questions)
    prompt = SOLUTION_EXPLANATION_PROMPT.format(
        topic=topic,
        questions=questions_json,
        score=score
    )
    try:
        response = await query_model(prompt)
        if isinstance(response, list) and len(response) > 0:
            return response[0].get('generated_text', '')
        return ''
    except Exception as e:
        raise Exception(f"Failed to generate solution explanation: {e}")
```

---

## Mock Response Fallback

When Hugging Face API is unavailable, `huggingface_service.py` generates mock responses:

```python
def generate_mock_response(prompt: str):
    """
    Generates a dynamic mock response for development/testing when API is unavailable.
    """
    if "Generate 5 core concept" in prompt and "MCQ" in prompt:
        # Mock question generation
        topic = extract_topic_from_prompt(prompt)
        difficulty = "beginner"
        if "advanced" in prompt.lower():
            difficulty = "advanced"
        
        questions = generate_dynamic_questions(topic, difficulty)
        response_text = json.dumps(questions)
        return [{"generated_text": response_text}]
    
    elif "Act as an expert evaluator" in prompt:
        # Mock evaluation
        score = extract_score_from_prompt(prompt)
        
        # Determine strengths/weaknesses based on score
        if score < 50:
            strengths = ["Effort to learn", "Willingness to participate"]
            weak_areas = ["Conceptual understanding", "Practical application"]
            level = "Beginner"
        else:
            strengths = ["Good understanding", "Problem-solving"]
            weak_areas = ["Advanced topics", "Edge cases"]
            level = "Intermediate"
        
        response_text = json.dumps({
            "score": score,
            "strengths": strengths,
            "weak_areas": weak_areas,
            "level": level
        })
        return [{"generated_text": response_text}]
    
    # ... more cases for analysis, solutions, roadmaps, challenges ...
```

---

## Summary

The entire workflow is orchestrated through:

1. **learning.py** - API endpoints that handle HTTP requests
2. **services/* ** - Business logic that calls LLMs appropriately
3. **huggingface_service.py** - Low-level API calls to Hugging Face
4. **prompts.py** - Carefully crafted prompt templates
5. **Mock fallback** - Ensures app works even without API

Each stage uses the most appropriate model:
- **Question Generation**: Mistral 7B (fast, sufficient)
- **Evaluation**: Llama 70B (high-quality judgment)
- **Everything Else**: Mistral 7B (balanced)
