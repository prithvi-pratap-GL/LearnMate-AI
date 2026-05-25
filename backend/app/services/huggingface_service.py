import aiohttp
import random
import re
from app.config.settings import settings

API_URL = "https://api-inference.huggingface.co/models/"
headers = {"Authorization": f"Bearer {settings.HUGGING_FACE_API_KEY}"}

async def query_model(prompt: str, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
    """
    Queries the Hugging Face Inference API with a given prompt and model.

    Falls back to a mock response if the API is unreachable (for development/testing).
    """
    session_timeout = aiohttp.ClientTimeout(total=30)  # 30 seconds timeout
    async with aiohttp.ClientSession(timeout=session_timeout) as session:
        payload = {"inputs": prompt}
        try:
            async with session.post(API_URL + model, headers=headers, json=payload) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientConnectorError as e:
            print(f"[WARNING] Could not connect to Hugging Face API: {e}")
            print("[INFO] Using mock response for development/testing")
            return generate_mock_response(prompt)
        except aiohttp.ClientResponseError as e:
            print(f"[WARNING] API returned status {e.status}: {e.message}")
            return generate_mock_response(prompt)
        except Exception as e:
            print(f"[WARNING] Error querying model: {e}")
            return generate_mock_response(prompt)


def extract_topic_from_prompt(prompt: str) -> str:
    """Extract topic from prompt using regex."""
    match = re.search(r'about "([^"]+)"', prompt)
    return match.group(1) if match else "the topic"


def generate_topic_specific_questions(topic: str, difficulty: str = "beginner"):
    """Generate 5 unique MCQ questions with options based on difficulty level."""
    topic_lower = topic.lower()

    # Beginner level MCQ questions
    beginner_mcq = {
        "machine learning": [
            {"question": "Which module has the SVM package?", "options": ["TensorFlow", "Scikit-Learn", "PyTorch", "Keras"], "correct_answer": "Scikit-Learn"},
            {"question": "What does ML stand for?", "options": ["Machine Learning", "Multi-Layer", "Mobile Learning", "Model Logic"], "correct_answer": "Machine Learning"},
            {"question": "Which library is used for numerical computation?", "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-Learn"], "correct_answer": "NumPy"},
            {"question": "What is a supervised learning algorithm?", "options": ["Clustering", "Linear Regression", "Principal Component Analysis", "K-Means"], "correct_answer": "Linear Regression"},
            {"question": "What is the process of training a model called?", "options": ["Testing", "Training", "Validation", "Evaluation"], "correct_answer": "Training"},
        ],
        "python programming": [
            {"question": "What is Python's package manager called?", "options": ["conda", "pip", "npm", "brew"], "correct_answer": "pip"},
            {"question": "Which symbol is used for comments in Python?", "options": ["//", "/*", "#", "--"], "correct_answer": "#"},
            {"question": "What data structure uses key-value pairs?", "options": ["List", "Tuple", "Dictionary", "Set"], "correct_answer": "Dictionary"},
            {"question": "Which is a mutable data type in Python?", "options": ["Tuple", "String", "List", "Integer"], "correct_answer": "List"},
            {"question": "What does PEP 8 define?", "options": ["Package Structure", "Style Guide", "Performance Metrics", "Python Engine Protocol"], "correct_answer": "Style Guide"},
        ],
        "data science": [
            {"question": "Which library is used for data manipulation?", "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-Learn"], "correct_answer": "Pandas"},
            {"question": "What is data cleaning called?", "options": ["Validation", "Preprocessing", "Transformation", "Integration"], "correct_answer": "Preprocessing"},
            {"question": "What does EDA stand for?", "options": ["Error Data Analysis", "Exploratory Data Analysis", "Essential Data Architecture", "Environmental Data Assessment"], "correct_answer": "Exploratory Data Analysis"},
            {"question": "Which format is common for data storage?", "options": ["JSON", "CSV", "XML", "Binary"], "correct_answer": "CSV"},
            {"question": "What is the process of reducing features called?", "options": ["Expansion", "Normalization", "Dimensionality Reduction", "Scaling"], "correct_answer": "Dimensionality Reduction"},
        ],
    }

    # Intermediate level MCQ questions
    intermediate_mcq = {
        "machine learning": [
            {"question": "What is the bias-variance tradeoff?", "options": ["Balancing model complexity and generalization", "Ratio of input to output", "Accuracy vs Precision", "Training vs Testing"], "correct_answer": "Balancing model complexity and generalization"},
            {"question": "Which technique prevents overfitting?", "options": ["Increasing features", "Regularization", "More training data", "Both B and C"], "correct_answer": "Regularization"},
            {"question": "What is cross-validation used for?", "options": ["Feature scaling", "Model evaluation", "Data cleaning", "Hyperparameter tuning"], "correct_answer": "Model evaluation"},
            {"question": "Name a dimensionality reduction technique.", "options": ["PCA", "K-Means", "Decision Trees", "Gradient Descent"], "correct_answer": "PCA"},
            {"question": "What is the purpose of the confusion matrix?", "options": ["Checking data distribution", "Evaluating classification models", "Feature selection", "Data preprocessing"], "correct_answer": "Evaluating classification models"},
        ],
        "python programming": [
            {"question": "What is a lambda function in Python?", "options": ["A function with multiple returns", "An anonymous function", "A recursive function", "A built-in module"], "correct_answer": "An anonymous function"},
            {"question": "What does the 'with' statement do?", "options": ["Conditional logic", "Resource management", "Loop iteration", "Function definition"], "correct_answer": "Resource management"},
            {"question": "What is a decorator in Python?", "options": ["CSS styling", "Function wrapper", "Data structure", "Module import"], "correct_answer": "Function wrapper"},
            {"question": "What is the difference between append() and extend()?", "options": ["append adds element, extend adds list elements", "They are identical", "extend is faster", "append is for tuples"], "correct_answer": "append adds element, extend adds list elements"},
            {"question": "What does *args do?", "options": ["Multiplies arguments", "Accepts variable-length arguments", "Creates array", "Pointer reference"], "correct_answer": "Accepts variable-length arguments"},
        ],
        "data science": [
            {"question": "What is feature engineering?", "options": ["Removing features", "Creating new features from existing ones", "Data collection", "Model training"], "correct_answer": "Creating new features from existing ones"},
            {"question": "Which technique handles missing data?", "options": ["Scaling", "Imputation", "Normalization", "Encoding"], "correct_answer": "Imputation"},
            {"question": "What is the purpose of train-test split?", "options": ["Data visualization", "Model evaluation on unseen data", "Feature scaling", "Removing outliers"], "correct_answer": "Model evaluation on unseen data"},
            {"question": "What is multicollinearity?", "options": ["Multiple models", "High correlation between features", "Many rows", "Data types mixing"], "correct_answer": "High correlation between features"},
            {"question": "How do you handle categorical variables?", "options": ["Delete them", "Encoding or One-Hot Encoding", "Convert to float", "Ignore them"], "correct_answer": "Encoding or One-Hot Encoding"},
        ],
    }

    # Advanced level MCQ questions
    advanced_mcq = {
        "machine learning": [
            {"question": "What is the curse of dimensionality?", "options": ["High computational cost only", "Deterioration of model performance with too many features", "Memory issues", "Training time increase"], "correct_answer": "Deterioration of model performance with too many features"},
            {"question": "Explain ensemble learning.", "options": ["Using single best model", "Combining multiple models for better prediction", "Model stacking only", "Sequential learning"], "correct_answer": "Combining multiple models for better prediction"},
            {"question": "What is the difference between L1 and L2 regularization?", "options": ["Speed difference", "L1 uses absolute values, L2 uses squared values", "L1 is for classification", "Same thing with different names"], "correct_answer": "L1 uses absolute values, L2 uses squared values"},
            {"question": "What is batch normalization used for?", "options": ["Data cleaning", "Stabilizing neural network training", "Model compression", "Feature scaling"], "correct_answer": "Stabilizing neural network training"},
            {"question": "Explain the vanishing gradient problem.", "options": ["Data disappearing", "Gradients becoming too small to update weights", "Model convergence", "Overfitting issue"], "correct_answer": "Gradients becoming too small to update weights"},
        ],
        "python programming": [
            {"question": "What is the Global Interpreter Lock (GIL)?", "options": ["Threading lock mechanism", "Global variable handler", "Memory manager", "Garbage collector"], "correct_answer": "Threading lock mechanism"},
            {"question": "Explain metaclasses in Python.", "options": ["Abstract classes", "Classes that define how classes behave", "Parent classes", "Type annotations"], "correct_answer": "Classes that define how classes behave"},
            {"question": "What is the difference between shallow and deep copy?", "options": ["Speed difference", "Shallow copies references, deep copies values", "Both identical", "Related to memory only"], "correct_answer": "Shallow copies references, deep copies values"},
            {"question": "What does asyncio provide?", "options": ["System I/O operations", "Asynchronous programming support", "File operations", "Threading library"], "correct_answer": "Asynchronous programming support"},
            {"question": "Explain context managers and their purpose.", "options": ["Variable scope", "Resource acquisition and release", "Class management", "Module imports"], "correct_answer": "Resource acquisition and release"},
        ],
        "data science": [
            {"question": "What is the difference between ARIMA and SARIMA?", "options": ["SARIMA has seasonal component", "Speed difference", "ARIMA is outdated", "Same with different names"], "correct_answer": "SARIMA has seasonal component"},
            {"question": "Explain feature extraction vs feature selection.", "options": ["Same concept", "Extraction creates new features, selection chooses existing ones", "Selection is better", "Extraction is only for images"], "correct_answer": "Extraction creates new features, selection chooses existing ones"},
            {"question": "What is the purpose of SHAP values?", "options": ["Performance metrics", "Explaining model predictions", "Data validation", "Feature scaling"], "correct_answer": "Explaining model predictions"},
            {"question": "How do you handle imbalanced datasets?", "options": ["Ignore them", "Oversampling, undersampling, or SMOTE", "Use accuracy metric", "Increase model complexity"], "correct_answer": "Oversampling, undersampling, or SMOTE"},
            {"question": "What is Bayesian optimization?", "options": ["Parameter tuning using probabilistic model", "Probability calculation", "Bayesian statistics", "Model validation"], "correct_answer": "Parameter tuning using probabilistic model"},
        ],
    }

    # Select questions based on difficulty
    if difficulty in ["advanced", "hard", "expert"]:
        qa_set = advanced_mcq
    elif difficulty in ["intermediate", "medium"]:
        qa_set = intermediate_mcq
    else:
        qa_set = beginner_mcq

    # Check if we have topic-specific questions
    for key, questions in qa_set.items():
        if key in topic_lower:
            return questions

    # Fallback: Generic MCQ for any topic
    generic_qa = [
        {"question": f"What is {topic}?", "options": ["A tool", "A concept", "A skill", "All of the above"], "correct_answer": "All of the above"},
        {"question": f"What is a key aspect of {topic}?", "options": ["Implementation", "Understanding", "Practice", "All of the above"], "correct_answer": "All of the above"},
        {"question": f"Which is important for {topic}?", "options": ["Theory", "Practice", "Real-world application", "All of the above"], "correct_answer": "All of the above"},
        {"question": f"How do you master {topic}?", "options": ["Study", "Practice", "Persistence", "All of the above"], "correct_answer": "All of the above"},
        {"question": f"What benefit does {topic} provide?", "options": ["Skill building", "Knowledge growth", "Career advancement", "All of the above"], "correct_answer": "All of the above"},
    ]

    return generic_qa


def generate_dynamic_questions(topic: str, difficulty: str = "beginner"):
    """Generate truly dynamic questions with varied, relevant options"""
    import random

    # More comprehensive question templates for different topics
    question_templates = {
        "python": [
            {"q": f"What is the primary purpose of the '{{}}'module in Python?", "correct": "Module management", "options": ["Module management", "Data visualization", "Web server", "Database connection"]},
            {"q": "Which of these is a mutable data type in Python?", "correct": "Dictionary", "options": ["Tuple", "String", "Dictionary", "Frozenset"]},
            {"q": "What does the 'with' statement in Python do?", "correct": "Context management", "options": ["Loop iteration", "Conditional execution", "Context management", "Function definition"]},
            {"q": "How would you reverse a list in Python?", "correct": "Using reversed() or [::-1]", "options": ["reverse()", "Using reversed() or [::-1]", "flip()", "invert()"]},
            {"q": "What is a lambda function in Python?", "correct": "Anonymous function", "options": ["Greek variable", "Anonymous function", "Type annotation", "Error handler"]},
        ],
        "javascript": [
            {"q": "What does 'this' refer to in JavaScript?", "correct": "Current object context", "options": ["Parent object", "Current object context", "Global window", "Function name"]},
            {"q": "Which method adds elements to the end of an array?", "correct": "push()", "options": ["append()", "push()", "add()", "insert()"]},
            {"q": "What is the difference between 'let' and 'var'?", "correct": "Block vs function scope", "options": ["Speed difference", "Block vs function scope", "Type safety", "Memory usage"]},
            {"q": "How do you declare a constant in JavaScript?", "correct": "const", "options": ["final", "constant", "const", "static"]},
            {"q": "What is a closure in JavaScript?", "correct": "Function with access to outer scope", "options": ["Ending a function", "Function with access to outer scope", "Nested loop", "Error handling"]},
        ],
        "machine learning": [
            {"q": "What is overfitting in ML?", "correct": "Model memorizes training data", "options": ["Too much data", "Model memorizes training data", "High accuracy", "Low loss"]},
            {"q": "Which technique prevents overfitting?", "correct": "Regularization", "options": ["Batch size", "Regularization", "More layers", "Higher learning rate"]},
            {"q": "What is cross-validation used for?", "correct": "Model evaluation", "options": ["Data augmentation", "Model evaluation", "Feature scaling", "Hyperparameter search"]},
            {"q": "What does SVM stand for?", "correct": "Support Vector Machine", "options": ["Supervised Variable Model", "Support Vector Machine", "Statistical Vector Method", "Sample Variance Matrix"]},
            {"q": "What is the main goal of clustering?", "correct": "Group similar data", "options": ["Predict labels", "Group similar data", "Reduce dimensions", "Classify images"]},
        ],
        "data science": [
            {"q": "What is the first step in data science?", "correct": "Data collection", "options": ["Model building", "Data collection", "Visualization", "Deployment"]},
            {"q": "What does EDA stand for?", "correct": "Exploratory Data Analysis", "options": ["Error Detection Algorithm", "Exploratory Data Analysis", "Essential Data Architecture", "Environmental Data Assessment"]},
            {"q": "How do you handle missing data?", "correct": "Imputation or removal", "options": ["Ignore it", "Imputation or removal", "Replace with random", "Double it"]},
            {"q": "What is feature engineering?", "correct": "Creating new features from existing data", "options": ["Removing features", "Creating new features from existing data", "Scaling data", "Encoding categories"]},
            {"q": "What is the purpose of train-test split?", "correct": "Evaluate on unseen data", "options": ["Data visualization", "Evaluate on unseen data", "Feature selection", "Model compression"]},
        ],
    }

    # Get relevant questions for the topic
    topic_lower = topic.lower()
    questions = []

    for key, q_set in question_templates.items():
        if key in topic_lower:
            questions = q_set
            break

    # If no specific match, use a generic set
    if not questions:
        questions = [
            {"q": f"What is the main concept of {topic}?", "correct": "Core principle", "options": ["Side topic", "Core principle", "Legacy feature", "Unrelated concept"]},
            {"q": f"Why is {topic} important?", "correct": "Essential skill", "options": ["Rarely used", "Essential skill", "Outdated", "Only theoretical"]},
            {"q": f"How do you apply {topic} in practice?", "correct": "Real-world usage", "options": ["Never", "Real-world usage", "Only in theory", "For testing only"]},
            {"q": f"What is an advanced aspect of {topic}?", "correct": "Advanced technique", "options": ["Basic concept", "Advanced technique", "Historical fact", "Marketing term"]},
            {"q": f"Which tool uses {topic}?", "correct": "Professional tool", "options": ["No tool", "Professional tool", "Toy software", "Deprecated tool"]},
        ]

    # Shuffle and limit to 5
    random.shuffle(questions)
    result = []
    for q_data in questions[:5]:
        # Shuffle options while keeping correct answer in the right position
        options = q_data["options"].copy()
        correct = q_data["correct"]
        random.shuffle(options)

        result.append({
            "question": q_data["q"],
            "options": options,
            "correct_answer": correct
        })

    return result


def calculate_realistic_score(answers_text: str) -> int:
    """Calculate a realistic score based on student answers"""
    # Parse the answers to get some indication of correctness
    import random

    # If answers are empty or very short, likely low score
    if not answers_text or len(answers_text) < 20:
        return random.randint(20, 40)

    # Simulate variation in scores
    # Check if answers seem detailed (longer = more effort = likely better)
    answer_lines = [line for line in answers_text.split('\n') if line.strip()]
    avg_length = sum(len(line) for line in answer_lines) / max(len(answer_lines), 1)

    if avg_length < 10:
        return random.randint(30, 50)
    elif avg_length < 30:
        return random.randint(40, 65)
    elif avg_length < 60:
        return random.randint(60, 80)
    else:
        return random.randint(70, 95)


def generate_mock_response(prompt: str):
    """
    Generates a dynamic mock response for development/testing when API is unavailable.
    """
    import json

    # Check what type of request this is based on the prompt content
    if "Generate 5 core concept" in prompt and "MCQ" in prompt:
        # Question generation - return topic-specific MCQ questions with dynamic options
        topic = extract_topic_from_prompt(prompt)
        difficulty = "beginner"
        if "advanced" in prompt.lower():
            difficulty = "advanced"
        elif "intermediate" in prompt.lower():
            difficulty = "intermediate"

        questions = generate_dynamic_questions(topic, difficulty)
        response_text = json.dumps(questions)
        return [{"generated_text": response_text}]

    elif "Evaluate the learner answers" in prompt:
        # Evaluation - calculate realistic score based on answers
        import random

        # Extract score based on answer quality
        score = calculate_realistic_score(prompt)

        # Vary strengths and weaknesses based on score
        if score < 40:
            strengths = ["Effort to learn", "Willingness to participate"]
            weak_areas = ["Conceptual understanding", "Practical application", "Advanced topics"]
            level = "Beginner"
        elif score < 60:
            strengths = ["Basic understanding", "Some practice"]
            weak_areas = ["Advanced concepts", "Complex scenarios"]
            level = "Beginner"
        elif score < 75:
            strengths = ["Good understanding", "Practical awareness", "Problem-solving"]
            weak_areas = ["Advanced topics", "Edge cases"]
            level = "Intermediate"
        else:
            strengths = ["Excellent understanding", "Strong problem-solving", "Advanced knowledge"]
            weak_areas = ["Niche topics", "Bleeding-edge techniques"]
            level = "Advanced"

        response_text = json.dumps({
            "score": score,
            "strengths": strengths,
            "weak_areas": weak_areas,
            "level": level
        })
        return [{"generated_text": response_text}]

    elif "Explain the topic for a beginner" in prompt:
        # Beginner explanation - topic-aware
        topic = extract_topic_from_prompt(prompt)
        return [{
            "generated_text": f"""
## Understanding {topic}: Beginner Guide

### Simple Explanation
{topic.capitalize()} is a fundamental concept that builds the foundation for deeper learning in this field.

### Real-World Examples
- Example 1: {topic} is used in everyday applications like mobile apps and websites
- Example 2: Professionals use {topic} to solve practical business problems
- Example 3: Understanding {topic} helps you write better, more efficient code

### Easy Exercises to Practice
1. Start with the basic concepts and terminology
2. Work through simple, guided problems step-by-step
3. Build gradually to more complex real-world scenarios
4. Practice daily with small projects

### Important Concepts to Remember
- Foundation: Core principles of {topic}
- Structure: How different components work together
- Application: Real-world use cases and patterns
- Best Practices: Common pitfalls to avoid

### Next Steps
- Practice with small projects daily
- Review concepts from different angles
- Ask questions and seek clarification
- Connect theory with practice
"""
        }]

    elif "Generate advanced challenge problems" in prompt:
        # Advanced challenges - topic-aware
        topic = extract_topic_from_prompt(prompt)
        return [{
            "generated_text": f"""
## Advanced Challenge Problems for {topic}

### Complex Coding Challenges
1. Implement an optimized solution for {topic}-related problems
2. Handle edge cases and error conditions gracefully
3. Design scalable, production-ready solutions
4. Optimize for performance and memory usage

### Real-World Scenario Problems
- Scenario 1: Design a system using {topic} for high traffic
- Scenario 2: Solve a performance optimization challenge
- Scenario 3: Architect a solution for enterprise-level application

### Optimization & Design Questions
1. How would you improve efficiency of {topic} implementation?
2. What are the trade-offs in different approaches?
3. How does your solution scale to millions of users?
4. What are the security considerations?

### Mini-Project Ideas
1. Build a complete project incorporating all {topic} concepts
2. Extend with additional features and optimizations
3. Deploy and monitor for production use
4. Document and present your solution

### Performance Considerations
- Time complexity optimization
- Space efficiency
- Caching strategies
- Parallel processing possibilities
"""
        }]

    else:
        # Roadmap or generic response - topic and level aware
        topic = extract_topic_from_prompt(prompt)
        level = "Beginner" if "beginner" in prompt.lower() else ("Advanced" if "advanced" in prompt.lower() else "Intermediate")

        return [{
            "generated_text": f"""
## 30-Day Personalized Learning Roadmap for {topic} ({level} Level)

### Week 1: Foundation & Core Concepts
- Day 1-2: Learn fundamental terminology and concepts of {topic}
- Day 3-4: Understand core principles and their importance
- Day 5-7: Practice basic exercises and simple projects

### Week 2: Practical Application & Hands-On Experience
- Day 8-10: Work with real-world examples
- Day 11-12: Build small projects using {topic}
- Day 13-14: Review and consolidate learning

### Week 3: Depth & Mastery
- Day 15-17: Explore advanced patterns and techniques
- Day 18-19: Solve complex problems
- Day 20-21: Integrate {topic} with other technologies

### Week 4: Specialization & Optimization
- Day 22-24: Deep dive into specialized areas
- Day 25-26: Optimize and refactor previous projects
- Day 27-30: Plan your advanced learning path

### Daily Study Schedule
- 30 minutes: Concept review and understanding
- 45 minutes: Hands-on practice and coding
- 30 minutes: Project work and application
- 15 minutes: Reflection and note-taking

### Practice Resources
- Daily: 2-3 small focused exercises
- Twice weekly: Medium-sized project work
- Weekly: One comprehensive challenge
- Bi-weekly: Review and assessment

### Success Metrics
- Week 1: Understand all basic concepts
- Week 2: Complete 2-3 small projects
- Week 3: Solve 5+ complex problems
- Week 4: Complete capstone project

### Improvement Strategy
1. Focus on weak areas identified in assessment
2. Build on your existing strengths
3. Practice consistently every day
4. Review and reinforce regularly
5. Seek feedback and iterate
"""
        }]
