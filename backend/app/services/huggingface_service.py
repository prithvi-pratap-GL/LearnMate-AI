import logging
import aiohttp
import random
import re
from app.config.settings import settings

from openai import AsyncOpenAI
from app.config.settings import settings

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {settings.HUGGING_FACE_API_KEY}",
    "Content-Type": "application/json",
}


log = logging.getLogger(__name__)


# async def query_model(
#     prompt: str, model: str = "meta-llama/Llama-3.1-8B-Instruct:novita"
# ):
#     """
#     Query HF Router using Chat Completions API.
#     """

#     session_timeout = aiohttp.ClientTimeout(total=60)

#     payload = {
#         "model": model,
#         "messages": [{"role": "user", "content": prompt}],
#         "temperature": 0.7,
#         "max_tokens": 1200,
#     }

#     try:

#         async with aiohttp.ClientSession(timeout=session_timeout) as session:

#             async with session.post(API_URL, headers=headers, json=payload) as response:

#                 response.raise_for_status()

#                 data = await response.json()

#                 generated_text = data["choices"][0]["message"]["content"]

#                 return [{"generated_text": generated_text}]

#     except aiohttp.ClientResponseError as e:
#         log.error(f"HF Router HTTP Error {e.status}: {e.message}")

#         if settings.DEBUG:
#             return generate_mock_response(prompt)

#         raise

#     except aiohttp.ClientError as e:
#         log.error(f"HF Router Connection Error: {e}")

#         if settings.DEBUG:
#             return generate_mock_response(prompt)

#         raise

#     except Exception as e:
#         log.exception(f"Unexpected model error: {e}")

#         if settings.DEBUG:
#             return generate_mock_response(prompt)

#         raise


async def query_model(
    prompt: str,
    model: str = "meta-llama/Llama-3.1-8B-Instruct:novita",
):
    """
    Query HF Router using Chat Completions API.
    """

    session_timeout = aiohttp.ClientTimeout(total=60)

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1200,
    }

    try:

        async with aiohttp.ClientSession(timeout=session_timeout) as session:

            async with session.post(
                API_URL,
                headers=headers,
                json=payload,
            ) as response:

                response.raise_for_status()

                data = await response.json()

                generated_text = data["choices"][0]["message"]["content"]

                # REAL LLM RESPONSE
                return [{"generated_text": generated_text}]

    except aiohttp.ClientResponseError as e:

        log.error(f"HF Router HTTP Error " f"{e.status}: {e.message}")

        if settings.DEBUG:

            return {
                "mock": True,
                "data": generate_mock_response(prompt),
            }

        raise

    except aiohttp.ClientError as e:

        log.error(f"HF Router Connection Error: {e}")

        if settings.DEBUG:

            return {
                "mock": True,
                "data": generate_mock_response(prompt),
            }

        raise

    except Exception as e:

        log.exception(f"Unexpected model error: {e}")

        if settings.DEBUG:

            return {
                "mock": True,
                "data": generate_mock_response(prompt),
            }

        raise


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
            {
                "question": "Which module has the SVM package?",
                "options": ["TensorFlow", "Scikit-Learn", "PyTorch", "Keras"],
                "correct_answer": "Scikit-Learn",
            },
            {
                "question": "What does ML stand for?",
                "options": [
                    "Machine Learning",
                    "Multi-Layer",
                    "Mobile Learning",
                    "Model Logic",
                ],
                "correct_answer": "Machine Learning",
            },
            {
                "question": "Which library is used for numerical computation?",
                "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-Learn"],
                "correct_answer": "NumPy",
            },
            {
                "question": "What is a supervised learning algorithm?",
                "options": [
                    "Clustering",
                    "Linear Regression",
                    "Principal Component Analysis",
                    "K-Means",
                ],
                "correct_answer": "Linear Regression",
            },
            {
                "question": "What is the process of training a model called?",
                "options": ["Testing", "Training", "Validation", "Evaluation"],
                "correct_answer": "Training",
            },
        ],
        "python programming": [
            {
                "question": "What is Python's package manager called?",
                "options": ["conda", "pip", "npm", "brew"],
                "correct_answer": "pip",
            },
            {
                "question": "Which symbol is used for comments in Python?",
                "options": ["//", "/*", "#", "--"],
                "correct_answer": "#",
            },
            {
                "question": "What data structure uses key-value pairs?",
                "options": ["List", "Tuple", "Dictionary", "Set"],
                "correct_answer": "Dictionary",
            },
            {
                "question": "Which is a mutable data type in Python?",
                "options": ["Tuple", "String", "List", "Integer"],
                "correct_answer": "List",
            },
            {
                "question": "What does PEP 8 define?",
                "options": [
                    "Package Structure",
                    "Style Guide",
                    "Performance Metrics",
                    "Python Engine Protocol",
                ],
                "correct_answer": "Style Guide",
            },
        ],
        "data science": [
            {
                "question": "Which library is used for data manipulation?",
                "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-Learn"],
                "correct_answer": "Pandas",
            },
            {
                "question": "What is data cleaning called?",
                "options": [
                    "Validation",
                    "Preprocessing",
                    "Transformation",
                    "Integration",
                ],
                "correct_answer": "Preprocessing",
            },
            {
                "question": "What does EDA stand for?",
                "options": [
                    "Error Data Analysis",
                    "Exploratory Data Analysis",
                    "Essential Data Architecture",
                    "Environmental Data Assessment",
                ],
                "correct_answer": "Exploratory Data Analysis",
            },
            {
                "question": "Which format is common for data storage?",
                "options": ["JSON", "CSV", "XML", "Binary"],
                "correct_answer": "CSV",
            },
            {
                "question": "What is the process of reducing features called?",
                "options": [
                    "Expansion",
                    "Normalization",
                    "Dimensionality Reduction",
                    "Scaling",
                ],
                "correct_answer": "Dimensionality Reduction",
            },
        ],
    }

    # Intermediate level MCQ questions
    intermediate_mcq = {
        "machine learning": [
            {
                "question": "What is the bias-variance tradeoff?",
                "options": [
                    "Balancing model complexity and generalization",
                    "Ratio of input to output",
                    "Accuracy vs Precision",
                    "Training vs Testing",
                ],
                "correct_answer": "Balancing model complexity and generalization",
            },
            {
                "question": "Which technique prevents overfitting?",
                "options": [
                    "Increasing features",
                    "Regularization",
                    "More training data",
                    "Both B and C",
                ],
                "correct_answer": "Regularization",
            },
            {
                "question": "What is cross-validation used for?",
                "options": [
                    "Feature scaling",
                    "Model evaluation",
                    "Data cleaning",
                    "Hyperparameter tuning",
                ],
                "correct_answer": "Model evaluation",
            },
            {
                "question": "Name a dimensionality reduction technique.",
                "options": ["PCA", "K-Means", "Decision Trees", "Gradient Descent"],
                "correct_answer": "PCA",
            },
            {
                "question": "What is the purpose of the confusion matrix?",
                "options": [
                    "Checking data distribution",
                    "Evaluating classification models",
                    "Feature selection",
                    "Data preprocessing",
                ],
                "correct_answer": "Evaluating classification models",
            },
        ],
        "python programming": [
            {
                "question": "What is a lambda function in Python?",
                "options": [
                    "A function with multiple returns",
                    "An anonymous function",
                    "A recursive function",
                    "A built-in module",
                ],
                "correct_answer": "An anonymous function",
            },
            {
                "question": "What does the 'with' statement do?",
                "options": [
                    "Conditional logic",
                    "Resource management",
                    "Loop iteration",
                    "Function definition",
                ],
                "correct_answer": "Resource management",
            },
            {
                "question": "What is a decorator in Python?",
                "options": [
                    "CSS styling",
                    "Function wrapper",
                    "Data structure",
                    "Module import",
                ],
                "correct_answer": "Function wrapper",
            },
            {
                "question": "What is the difference between append() and extend()?",
                "options": [
                    "append adds element, extend adds list elements",
                    "They are identical",
                    "extend is faster",
                    "append is for tuples",
                ],
                "correct_answer": "append adds element, extend adds list elements",
            },
            {
                "question": "What does *args do?",
                "options": [
                    "Multiplies arguments",
                    "Accepts variable-length arguments",
                    "Creates array",
                    "Pointer reference",
                ],
                "correct_answer": "Accepts variable-length arguments",
            },
        ],
        "data science": [
            {
                "question": "What is feature engineering?",
                "options": [
                    "Removing features",
                    "Creating new features from existing ones",
                    "Data collection",
                    "Model training",
                ],
                "correct_answer": "Creating new features from existing ones",
            },
            {
                "question": "Which technique handles missing data?",
                "options": ["Scaling", "Imputation", "Normalization", "Encoding"],
                "correct_answer": "Imputation",
            },
            {
                "question": "What is the purpose of train-test split?",
                "options": [
                    "Data visualization",
                    "Model evaluation on unseen data",
                    "Feature scaling",
                    "Removing outliers",
                ],
                "correct_answer": "Model evaluation on unseen data",
            },
            {
                "question": "What is multicollinearity?",
                "options": [
                    "Multiple models",
                    "High correlation between features",
                    "Many rows",
                    "Data types mixing",
                ],
                "correct_answer": "High correlation between features",
            },
            {
                "question": "How do you handle categorical variables?",
                "options": [
                    "Delete them",
                    "Encoding or One-Hot Encoding",
                    "Convert to float",
                    "Ignore them",
                ],
                "correct_answer": "Encoding or One-Hot Encoding",
            },
        ],
    }

    # Advanced level MCQ questions
    advanced_mcq = {
        "machine learning": [
            {
                "question": "What is the curse of dimensionality?",
                "options": [
                    "High computational cost only",
                    "Deterioration of model performance with too many features",
                    "Memory issues",
                    "Training time increase",
                ],
                "correct_answer": "Deterioration of model performance with too many features",
            },
            {
                "question": "Explain ensemble learning.",
                "options": [
                    "Using single best model",
                    "Combining multiple models for better prediction",
                    "Model stacking only",
                    "Sequential learning",
                ],
                "correct_answer": "Combining multiple models for better prediction",
            },
            {
                "question": "What is the difference between L1 and L2 regularization?",
                "options": [
                    "Speed difference",
                    "L1 uses absolute values, L2 uses squared values",
                    "L1 is for classification",
                    "Same thing with different names",
                ],
                "correct_answer": "L1 uses absolute values, L2 uses squared values",
            },
            {
                "question": "What is batch normalization used for?",
                "options": [
                    "Data cleaning",
                    "Stabilizing neural network training",
                    "Model compression",
                    "Feature scaling",
                ],
                "correct_answer": "Stabilizing neural network training",
            },
            {
                "question": "Explain the vanishing gradient problem.",
                "options": [
                    "Data disappearing",
                    "Gradients becoming too small to update weights",
                    "Model convergence",
                    "Overfitting issue",
                ],
                "correct_answer": "Gradients becoming too small to update weights",
            },
        ],
        "python programming": [
            {
                "question": "What is the Global Interpreter Lock (GIL)?",
                "options": [
                    "Threading lock mechanism",
                    "Global variable handler",
                    "Memory manager",
                    "Garbage collector",
                ],
                "correct_answer": "Threading lock mechanism",
            },
            {
                "question": "Explain metaclasses in Python.",
                "options": [
                    "Abstract classes",
                    "Classes that define how classes behave",
                    "Parent classes",
                    "Type annotations",
                ],
                "correct_answer": "Classes that define how classes behave",
            },
            {
                "question": "What is the difference between shallow and deep copy?",
                "options": [
                    "Speed difference",
                    "Shallow copies references, deep copies values",
                    "Both identical",
                    "Related to memory only",
                ],
                "correct_answer": "Shallow copies references, deep copies values",
            },
            {
                "question": "What does asyncio provide?",
                "options": [
                    "System I/O operations",
                    "Asynchronous programming support",
                    "File operations",
                    "Threading library",
                ],
                "correct_answer": "Asynchronous programming support",
            },
            {
                "question": "Explain context managers and their purpose.",
                "options": [
                    "Variable scope",
                    "Resource acquisition and release",
                    "Class management",
                    "Module imports",
                ],
                "correct_answer": "Resource acquisition and release",
            },
        ],
        "data science": [
            {
                "question": "What is the difference between ARIMA and SARIMA?",
                "options": [
                    "SARIMA has seasonal component",
                    "Speed difference",
                    "ARIMA is outdated",
                    "Same with different names",
                ],
                "correct_answer": "SARIMA has seasonal component",
            },
            {
                "question": "Explain feature extraction vs feature selection.",
                "options": [
                    "Same concept",
                    "Extraction creates new features, selection chooses existing ones",
                    "Selection is better",
                    "Extraction is only for images",
                ],
                "correct_answer": "Extraction creates new features, selection chooses existing ones",
            },
            {
                "question": "What is the purpose of SHAP values?",
                "options": [
                    "Performance metrics",
                    "Explaining model predictions",
                    "Data validation",
                    "Feature scaling",
                ],
                "correct_answer": "Explaining model predictions",
            },
            {
                "question": "How do you handle imbalanced datasets?",
                "options": [
                    "Ignore them",
                    "Oversampling, undersampling, or SMOTE",
                    "Use accuracy metric",
                    "Increase model complexity",
                ],
                "correct_answer": "Oversampling, undersampling, or SMOTE",
            },
            {
                "question": "What is Bayesian optimization?",
                "options": [
                    "Parameter tuning using probabilistic model",
                    "Probability calculation",
                    "Bayesian statistics",
                    "Model validation",
                ],
                "correct_answer": "Parameter tuning using probabilistic model",
            },
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
        {
            "question": f"What is {topic}?",
            "options": ["A tool", "A concept", "A skill", "All of the above"],
            "correct_answer": "All of the above",
        },
        {
            "question": f"What is a key aspect of {topic}?",
            "options": [
                "Implementation",
                "Understanding",
                "Practice",
                "All of the above",
            ],
            "correct_answer": "All of the above",
        },
        {
            "question": f"Which is important for {topic}?",
            "options": [
                "Theory",
                "Practice",
                "Real-world application",
                "All of the above",
            ],
            "correct_answer": "All of the above",
        },
        {
            "question": f"How do you master {topic}?",
            "options": ["Study", "Practice", "Persistence", "All of the above"],
            "correct_answer": "All of the above",
        },
        {
            "question": f"What benefit does {topic} provide?",
            "options": [
                "Skill building",
                "Knowledge growth",
                "Career advancement",
                "All of the above",
            ],
            "correct_answer": "All of the above",
        },
    ]

    return generic_qa


def generate_dynamic_questions(topic: str, difficulty: str = "beginner"):
    """Generate truly dynamic questions with varied, relevant options - completely different for each difficulty level"""
    import random

    # BEGINNER level questions (for Round 1)
    beginner_questions = {
        "python": [
            {
                "q": "What is Python's package manager called?",
                "correct": "pip",
                "options": ["conda", "pip", "npm", "brew"],
            },
            {
                "q": "Which symbol is used for comments in Python?",
                "correct": "#",
                "options": ["//", "/*", "#", "--"],
            },
            {
                "q": "What data structure uses key-value pairs?",
                "correct": "Dictionary",
                "options": ["List", "Tuple", "Dictionary", "Set"],
            },
            {
                "q": "Which is a mutable data type in Python?",
                "correct": "List",
                "options": ["Tuple", "String", "List", "Integer"],
            },
            {
                "q": "What does PEP 8 define?",
                "correct": "Style Guide",
                "options": [
                    "Package Structure",
                    "Style Guide",
                    "Performance Metrics",
                    "Python Engine Protocol",
                ],
            },
            {
                "q": "What is a variable in Python?",
                "correct": "Container for storing values",
                "options": [
                    "A function",
                    "Container for storing values",
                    "A class",
                    "An error",
                ],
            },
            {
                "q": "How do you create a list in Python?",
                "correct": "Using square brackets []",
                "options": [
                    "Using curly braces {}",
                    "Using parentheses ()",
                    "Using square brackets []",
                    "Using angle brackets <>",
                ],
            },
            {
                "q": "What does the print() function do?",
                "correct": "Displays output to console",
                "options": [
                    "Reads user input",
                    "Displays output to console",
                    "Deletes variables",
                    "Imports modules",
                ],
            },
            {
                "q": "What is an integer in Python?",
                "correct": "Whole number",
                "options": [
                    "Decimal number",
                    "Whole number",
                    "Text string",
                    "Boolean value",
                ],
            },
            {
                "q": "How do you define a function in Python?",
                "correct": "Using def keyword",
                "options": [
                    "Using function keyword",
                    "Using def keyword",
                    "Using lambda only",
                    "Using class only",
                ],
            },
        ],
        "javascript": [
            {
                "q": "What does JavaScript stand for?",
                "correct": "Standardized programming language",
                "options": [
                    "Java Script language",
                    "Standardized programming language",
                    "JavaScript Extension",
                    "Just A Script",
                ],
            },
            {
                "q": "How do you create a variable in JavaScript?",
                "correct": "Using var, let, or const",
                "options": [
                    "Using $ symbol",
                    "Using var, let, or const",
                    "Using # symbol",
                    "Using :: operator",
                ],
            },
            {
                "q": "What is an array in JavaScript?",
                "correct": "Ordered list of values",
                "options": [
                    "A single value",
                    "Ordered list of values",
                    "A function",
                    "A string",
                ],
            },
            {
                "q": "How do you add an element to an array?",
                "correct": "Using push() method",
                "options": [
                    "Using add() method",
                    "Using push() method",
                    "Using append() method",
                    "Using insert() method",
                ],
            },
            {
                "q": "What is a function in JavaScript?",
                "correct": "Reusable block of code",
                "options": [
                    "A variable",
                    "Reusable block of code",
                    "A loop",
                    "An object",
                ],
            },
            {
                "q": "How do you write a comment in JavaScript?",
                "correct": "// for single line or /* */ for multi-line",
                "options": [
                    "# for comments",
                    "-- for comments",
                    "// for single line or /* */ for multi-line",
                    "' for comments",
                ],
            },
            {
                "q": "What is the console.log() function used for?",
                "correct": "Printing output to console",
                "options": [
                    "Reading input",
                    "Printing output to console",
                    "Clearing the console",
                    "Deleting variables",
                ],
            },
            {
                "q": "What is undefined in JavaScript?",
                "correct": "Value of a variable that has no value",
                "options": [
                    "An error type",
                    "Value of a variable that has no value",
                    "A keyword",
                    "A number",
                ],
            },
            {
                "q": "How do you check if a value is null?",
                "correct": "Using === null",
                "options": [
                    "Using == empty",
                    "Using === null",
                    "Using null check",
                    "Using isEmpty()",
                ],
            },
            {
                "q": "What is a string in JavaScript?",
                "correct": "Sequence of characters",
                "options": [
                    "A number",
                    "Sequence of characters",
                    "A boolean",
                    "An array",
                ],
            },
        ],
        "machine learning": [
            {
                "q": "What does ML stand for?",
                "correct": "Machine Learning",
                "options": [
                    "Multi-Layer",
                    "Mobile Learning",
                    "Model Logic",
                    "Machine Learning",
                ],
            },
            {
                "q": "What is supervised learning?",
                "correct": "Learning with labeled data",
                "options": [
                    "Learning without labels",
                    "Learning with labeled data",
                    "Learning from images",
                    "Learning from text",
                ],
            },
            {
                "q": "What is a dataset?",
                "correct": "Collection of data for training",
                "options": [
                    "A single data point",
                    "Collection of data for training",
                    "A machine",
                    "A model",
                ],
            },
            {
                "q": "What is a feature in ML?",
                "correct": "Input variable used for prediction",
                "options": [
                    "Output result",
                    "Input variable used for prediction",
                    "A model",
                    "An error",
                ],
            },
            {
                "q": "What is training in ML?",
                "correct": "Process of teaching a model with data",
                "options": [
                    "Testing a model",
                    "Process of teaching a model with data",
                    "Deploying a model",
                    "Evaluating accuracy",
                ],
            },
            {
                "q": "What is NumPy used for?",
                "correct": "Numerical computations",
                "options": [
                    "Web development",
                    "Numerical computations",
                    "Game creation",
                    "Database management",
                ],
            },
            {
                "q": "What is Pandas used for?",
                "correct": "Data manipulation and analysis",
                "options": [
                    "Web frameworks",
                    "Data manipulation and analysis",
                    "Image processing",
                    "Text generation",
                ],
            },
            {
                "q": "What is a classifier?",
                "correct": "Algorithm that predicts categories",
                "options": [
                    "Tool for organizing files",
                    "Algorithm that predicts categories",
                    "Data processor",
                    "Error handler",
                ],
            },
            {
                "q": "What is accuracy in ML?",
                "correct": "Percentage of correct predictions",
                "options": [
                    "Speed of prediction",
                    "Percentage of correct predictions",
                    "Model size",
                    "Training time",
                ],
            },
            {
                "q": "What is a neural network?",
                "correct": "Network of connected nodes inspired by brain",
                "options": [
                    "Computer network",
                    "Network of connected nodes inspired by brain",
                    "A type of database",
                    "A web server",
                ],
            },
        ],
        "data science": [
            {
                "q": "What is data science?",
                "correct": "Field that extracts insights from data",
                "options": [
                    "Science of computers",
                    "Field that extracts insights from data",
                    "Data storage",
                    "Database design",
                ],
            },
            {
                "q": "What is the first step in data science?",
                "correct": "Data collection",
                "options": [
                    "Model building",
                    "Data collection",
                    "Visualization",
                    "Deployment",
                ],
            },
            {
                "q": "What does EDA stand for?",
                "correct": "Exploratory Data Analysis",
                "options": [
                    "Error Detection Algorithm",
                    "Exploratory Data Analysis",
                    "Essential Data Architecture",
                    "Environmental Data Assessment",
                ],
            },
            {
                "q": "What is data cleaning?",
                "correct": "Removing errors and inconsistencies",
                "options": [
                    "Deleting all data",
                    "Removing errors and inconsistencies",
                    "Encrypting data",
                    "Compressing data",
                ],
            },
            {
                "q": "What is visualization in data science?",
                "correct": "Creating charts and graphs",
                "options": [
                    "Writing code",
                    "Creating charts and graphs",
                    "Reading files",
                    "Training models",
                ],
            },
            {
                "q": "What is a CSV file?",
                "correct": "Comma-separated values file",
                "options": [
                    "Computer Specific Values",
                    "Comma-separated values file",
                    "Central Storage Vault",
                    "Code Syntax Validator",
                ],
            },
            {
                "q": "What is correlation?",
                "correct": "Relationship between two variables",
                "options": [
                    "A type of database",
                    "Relationship between two variables",
                    "An error type",
                    "A programming language",
                ],
            },
            {
                "q": "What is a null value?",
                "correct": "Missing or undefined data",
                "options": [
                    "Zero value",
                    "Missing or undefined data",
                    "Empty string",
                    "False boolean",
                ],
            },
            {
                "q": "What is normalization?",
                "correct": "Scaling data to standard range",
                "options": [
                    "Organizing files",
                    "Scaling data to standard range",
                    "Removing duplicates",
                    "Adding new data",
                ],
            },
            {
                "q": "What is a dashboard?",
                "correct": "Visual display of key metrics",
                "options": [
                    "Car control panel",
                    "Visual display of key metrics",
                    "Programming tool",
                    "Data file",
                ],
            },
        ],
    }

    # ADVANCED level questions (for Round 2)
    advanced_questions = {
        "python": [
            {
                "q": "What is the Global Interpreter Lock (GIL)?",
                "correct": "Threading mechanism that limits parallel execution",
                "options": [
                    "Global variable handler",
                    "Threading mechanism that limits parallel execution",
                    "Memory manager",
                    "Garbage collector",
                ],
            },
            {
                "q": "What are metaclasses in Python?",
                "correct": "Classes that define how classes behave",
                "options": [
                    "Abstract base classes",
                    "Classes that define how classes behave",
                    "Parent classes",
                    "Type annotations",
                ],
            },
            {
                "q": "What is the difference between shallow and deep copy?",
                "correct": "Shallow copies references, deep copies values",
                "options": [
                    "Speed difference",
                    "Shallow copies references, deep copies values",
                    "Both are identical",
                    "Related to memory allocation",
                ],
            },
            {
                "q": "What does asyncio provide?",
                "correct": "Asynchronous programming support",
                "options": [
                    "System I/O operations",
                    "Asynchronous programming support",
                    "File management",
                    "Threading utilities",
                ],
            },
            {
                "q": "What are context managers used for?",
                "correct": "Resource acquisition and release",
                "options": [
                    "Variable scope management",
                    "Resource acquisition and release",
                    "Class management",
                    "Module imports",
                ],
            },
            {
                "q": "What is a decorator in Python?",
                "correct": "Function that modifies another function",
                "options": [
                    "CSS styling",
                    "Function that modifies another function",
                    "Data structure",
                    "Module import",
                ],
            },
            {
                "q": "What does *args do?",
                "correct": "Accepts variable-length positional arguments",
                "options": [
                    "Multiplies arguments",
                    "Accepts variable-length positional arguments",
                    "Creates array",
                    "Pointer reference",
                ],
            },
            {
                "q": "What does **kwargs do?",
                "correct": "Accepts variable-length keyword arguments",
                "options": [
                    "Power operator",
                    "Accepts variable-length keyword arguments",
                    "XOR operation",
                    "Multiplication",
                ],
            },
            {
                "q": "What is a generator in Python?",
                "correct": "Function that yields values lazily",
                "options": [
                    "Random number creator",
                    "Function that yields values lazily",
                    "Data generator tool",
                    "Code generator",
                ],
            },
            {
                "q": "What is the with statement used for?",
                "correct": "Context management for resource handling",
                "options": [
                    "Conditional logic",
                    "Context management for resource handling",
                    "Loop iteration",
                    "Function definition",
                ],
            },
        ],
        "javascript": [
            {
                "q": "What is the event loop in JavaScript?",
                "correct": "Mechanism for executing asynchronous code",
                "options": [
                    "Error handling",
                    "Mechanism for executing asynchronous code",
                    "DOM manipulation",
                    "Module loading",
                ],
            },
            {
                "q": "What are closures in JavaScript?",
                "correct": "Functions with access to outer scope variables",
                "options": [
                    "Loop termination",
                    "Functions with access to outer scope variables",
                    "Error handling",
                    "Data structures",
                ],
            },
            {
                "q": "What is hoisting in JavaScript?",
                "correct": "Moving declarations to the top of scope",
                "options": [
                    "Lifting objects",
                    "Moving declarations to the top of scope",
                    "Error throwing",
                    "Variable assignment",
                ],
            },
            {
                "q": "What is the difference between Promise and async/await?",
                "correct": "async/await is cleaner syntax for Promises",
                "options": [
                    "Same thing",
                    "async/await is cleaner syntax for Promises",
                    "Promises are faster",
                    "No difference",
                ],
            },
            {
                "q": "What are prototypes in JavaScript?",
                "correct": "Objects from which other objects inherit",
                "options": [
                    "Test versions",
                    "Objects from which other objects inherit",
                    "Design patterns",
                    "API endpoints",
                ],
            },
            {
                "q": "What is the this keyword binding?",
                "correct": "Refers to object context of execution",
                "options": [
                    "Creates variables",
                    "Refers to object context of execution",
                    "Loops through data",
                    "Deletes properties",
                ],
            },
            {
                "q": "What are higher-order functions?",
                "correct": "Functions that take or return functions",
                "options": [
                    "Functions with many parameters",
                    "Functions that take or return functions",
                    "Complex calculations",
                    "Recursive functions",
                ],
            },
            {
                "q": "What is destructuring in JavaScript?",
                "correct": "Unpacking values from objects or arrays",
                "options": [
                    "Deleting data",
                    "Unpacking values from objects or arrays",
                    "Modifying structure",
                    "Rebuilding objects",
                ],
            },
            {
                "q": "What is the spread operator used for?",
                "correct": "Expanding iterables into individual elements",
                "options": [
                    "Mathematical division",
                    "Expanding iterables into individual elements",
                    "String operations",
                    "Object creation",
                ],
            },
            {
                "q": "What is currying in JavaScript?",
                "correct": "Converting function with multiple args into sequence of single-arg functions",
                "options": [
                    "Adding functions",
                    "Converting function with multiple args into sequence of single-arg functions",
                    "Error handling",
                    "Data transformation",
                ],
            },
        ],
        "machine learning": [
            {
                "q": "What is the curse of dimensionality?",
                "correct": "Performance degradation with too many features",
                "options": [
                    "Memory issues only",
                    "Performance degradation with too many features",
                    "Training time",
                    "Model complexity",
                ],
            },
            {
                "q": "What is ensemble learning?",
                "correct": "Combining multiple models for better predictions",
                "options": [
                    "Using single model",
                    "Combining multiple models for better predictions",
                    "Sequential training",
                    "Parallel processing",
                ],
            },
            {
                "q": "What is the difference between L1 and L2 regularization?",
                "correct": "L1 uses absolute values, L2 uses squared values",
                "options": [
                    "Speed difference",
                    "L1 uses absolute values, L2 uses squared values",
                    "L1 for classification",
                    "Same regularization",
                ],
            },
            {
                "q": "What is batch normalization?",
                "correct": "Normalizing layer inputs to stabilize training",
                "options": [
                    "Data cleaning",
                    "Normalizing layer inputs to stabilize training",
                    "Model compression",
                    "Batch processing",
                ],
            },
            {
                "q": "What is the vanishing gradient problem?",
                "correct": "Gradients becoming too small to update weights",
                "options": [
                    "Data disappearing",
                    "Gradients becoming too small to update weights",
                    "Model convergence",
                    "Overfitting",
                ],
            },
            {
                "q": "What is transfer learning?",
                "correct": "Using pre-trained models as starting point",
                "options": [
                    "Moving models between systems",
                    "Using pre-trained models as starting point",
                    "Transferring data",
                    "Model cloning",
                ],
            },
            {
                "q": "What is dropout in neural networks?",
                "correct": "Randomly disabling neurons to prevent overfitting",
                "options": [
                    "Removing layers",
                    "Randomly disabling neurons to prevent overfitting",
                    "Data dropping",
                    "Model pruning",
                ],
            },
            {
                "q": "What is backpropagation?",
                "correct": "Algorithm for calculating gradients in neural networks",
                "options": [
                    "Moving backwards",
                    "Algorithm for calculating gradients in neural networks",
                    "Reversing predictions",
                    "Error correction",
                ],
            },
            {
                "q": "What is attention mechanism?",
                "correct": "Mechanism to focus on relevant input parts",
                "options": [
                    "Error detection",
                    "Mechanism to focus on relevant input parts",
                    "Monitoring system",
                    "Debug tool",
                ],
            },
            {
                "q": "What is hyperparameter tuning?",
                "correct": "Optimizing model parameters before training",
                "options": [
                    "Training the model",
                    "Optimizing model parameters before training",
                    "Testing accuracy",
                    "Deployment process",
                ],
            },
        ],
        "data science": [
            {
                "q": "What is feature extraction vs feature selection?",
                "correct": "Extraction creates features, selection chooses existing ones",
                "options": [
                    "Same concept",
                    "Extraction creates features, selection chooses existing ones",
                    "Selection is always better",
                    "Extraction for images only",
                ],
            },
            {
                "q": "What is SHAP values used for?",
                "correct": "Explaining individual model predictions",
                "options": [
                    "Performance metrics",
                    "Explaining individual model predictions",
                    "Data validation",
                    "Feature scaling",
                ],
            },
            {
                "q": "How do you handle imbalanced datasets?",
                "correct": "Oversampling, undersampling, or SMOTE",
                "options": [
                    "Ignore them",
                    "Oversampling, undersampling, or SMOTE",
                    "Use accuracy",
                    "Increase complexity",
                ],
            },
            {
                "q": "What is Bayesian optimization?",
                "correct": "Parameter tuning using probabilistic model",
                "options": [
                    "Probability calculation",
                    "Parameter tuning using probabilistic model",
                    "Bayesian statistics",
                    "Model validation",
                ],
            },
            {
                "q": "What is the bias-variance tradeoff?",
                "correct": "Balancing model complexity and generalization",
                "options": [
                    "Input to output ratio",
                    "Balancing model complexity and generalization",
                    "Accuracy vs Precision",
                    "Training vs Testing",
                ],
            },
            {
                "q": "What is cross-validation used for?",
                "correct": "Evaluating model on multiple data splits",
                "options": [
                    "Data augmentation",
                    "Evaluating model on multiple data splits",
                    "Feature scaling",
                    "Hyperparameter search",
                ],
            },
            {
                "q": "What is ARIMA used for?",
                "correct": "Time series forecasting",
                "options": [
                    "Image processing",
                    "Time series forecasting",
                    "Text analysis",
                    "Classification",
                ],
            },
            {
                "q": "What is the Gini coefficient?",
                "correct": "Measure of impurity in decision trees",
                "options": [
                    "Statistical index",
                    "Measure of impurity in decision trees",
                    "Economic metric",
                    "Probability measure",
                ],
            },
            {
                "q": "What is multicollinearity?",
                "correct": "High correlation between features",
                "options": [
                    "Multiple models",
                    "High correlation between features",
                    "Many rows of data",
                    "Data type mixing",
                ],
            },
            {
                "q": "What is residual analysis?",
                "correct": "Analyzing prediction errors to improve model",
                "options": [
                    "Removing data",
                    "Analyzing prediction errors to improve model",
                    "Adding features",
                    "Scaling values",
                ],
            },
        ],
    }

    # Determine which question set to use based on difficulty
    topic_lower = topic.lower()

    if difficulty.lower() in ["advanced", "hard", "expert"]:
        question_pool = advanced_questions
    else:
        question_pool = beginner_questions

    # Get relevant questions for the topic
    questions = []
    for key, q_set in question_pool.items():
        if key in topic_lower:
            questions = q_set
            break

    # If no specific match, use a generic set
    if not questions:
        if difficulty.lower() in ["advanced", "hard", "expert"]:
            questions = [
                {
                    "q": f"What are advanced techniques in {topic}?",
                    "correct": "Specialized methods",
                    "options": [
                        "Basic methods",
                        "Specialized methods",
                        "Historical approach",
                        "Deprecated methods",
                    ],
                },
                {
                    "q": f"How do you optimize {topic} for production?",
                    "correct": "Performance tuning",
                    "options": [
                        "Add more data",
                        "Performance tuning",
                        "Increase complexity",
                        "Use defaults",
                    ],
                },
                {
                    "q": f"What are edge cases in {topic}?",
                    "correct": "Boundary conditions",
                    "options": [
                        "Main cases",
                        "Boundary conditions",
                        "Error types",
                        "Test cases",
                    ],
                },
                {
                    "q": f"How do you scale {topic} solutions?",
                    "correct": "Handling growth",
                    "options": [
                        "Reduce data",
                        "Handling growth",
                        "Simplify design",
                        "Use shortcuts",
                    ],
                },
                {
                    "q": f"What is architectural design for {topic}?",
                    "correct": "System design patterns",
                    "options": [
                        "Code structure",
                        "System design patterns",
                        "File organization",
                        "Naming conventions",
                    ],
                },
            ]
        else:
            questions = [
                {
                    "q": f"What is the definition of {topic}?",
                    "correct": "Formal definition",
                    "options": ["A tool", "Formal definition", "A skill", "A concept"],
                },
                {
                    "q": f"Why is {topic} important?",
                    "correct": "Essential knowledge",
                    "options": [
                        "Rarely used",
                        "Essential knowledge",
                        "Outdated",
                        "Theoretical",
                    ],
                },
                {
                    "q": f"How do you start learning {topic}?",
                    "correct": "Fundamentals first",
                    "options": [
                        "Advanced topics",
                        "Fundamentals first",
                        "Without practice",
                        "Random order",
                    ],
                },
                {
                    "q": f"What tools help with {topic}?",
                    "correct": "Supporting software",
                    "options": [
                        "Pen and paper",
                        "Supporting software",
                        "Nothing needed",
                        "Hardware only",
                    ],
                },
                {
                    "q": f"What is a real-world use of {topic}?",
                    "correct": "Practical application",
                    "options": [
                        "Never used",
                        "Practical application",
                        "Only theory",
                        "Only research",
                    ],
                },
            ]

    # Shuffle and limit to 5, ensuring uniqueness
    random.shuffle(questions)
    result = []
    seen_questions = set()

    for q_data in questions:
        q_text = q_data["q"].lower()
        if q_text not in seen_questions:
            seen_questions.add(q_text)
            # Shuffle options while keeping correct answer in the right position
            options = q_data["options"].copy()
            correct = q_data["correct"]
            random.shuffle(options)

            result.append(
                {"question": q_data["q"], "options": options, "correct_answer": correct}
            )

            if len(result) >= 5:
                break

    return result


def calculate_score_from_answers(questions_list):
    """Calculate score by comparing student answers against correct answers"""
    import random

    if not questions_list:
        return random.randint(20, 40)

    correct_count = 0

    # Compare each student answer with the correct answer
    for q in questions_list:
        student_answer = q.get("student_answer", "").strip().lower()
        correct_answer = q.get("correct_answer", "").strip().lower()

        # Direct match comparison
        if student_answer == correct_answer:
            correct_count += 1
        # Also handle case-insensitive partial matching for MCQ options
        elif student_answer in correct_answer or correct_answer in student_answer:
            correct_count += 1

    # Calculate percentage
    score = int((correct_count / len(questions_list)) * 100)
    return score


def generate_mock_response(prompt: str):
    """
    Generates a dynamic mock response for development/testing when API is unavailable.
    """
    import json
    import re

    print("\nthis call is reaching generate_mock_response(), these are mock questions")

    # Check what type of request this is based on the prompt content
    if "Generate 5" in prompt and "MCQ" in prompt:
        # Question generation - return topic-specific MCQ questions with dynamic options
        topic = extract_topic_from_prompt(prompt)
        difficulty = "beginner"
        # Check for specific difficulty level marker in prompt
        if "Difficulty Level: advanced" in prompt:
            difficulty = "advanced"
        elif "Difficulty Level: intermediate" in prompt:
            difficulty = "intermediate"
        elif "Difficulty Level: beginner" in prompt:
            difficulty = "beginner"

        questions = generate_dynamic_questions(topic, difficulty)
        response_text = json.dumps(questions)
        return [{"generated_text": response_text}]

    elif "Act as an expert evaluator" in prompt:
        # Evaluation using specialized judge model - more detailed analysis
        import random

        # Extract score from prompt (it should be in "Score: XX" format)
        score = 50
        score_match = re.search(r"Score: (\d+)", prompt)
        if score_match:
            score = int(score_match.group(1))

        # Extract topic for better evaluation
        topic = "the topic"
        topic_match = re.search(r"topic: ([^\n.]+)", prompt, re.IGNORECASE)
        if topic_match:
            topic = topic_match.group(1).strip()

        # Also try to extract questions JSON for fallback calculation
        json_match = re.search(r"\[.*?\]", prompt, re.DOTALL)
        questions_list = []
        if json_match:
            try:
                questions_list = json.loads(json_match.group())
            except:
                questions_list = []

        # Use the provided score or calculate from answers as fallback
        if score_match is None:
            score = (
                calculate_score_from_answers(questions_list)
                if questions_list
                else random.randint(20, 95)
            )

        # More nuanced evaluation logic based on score and topic
        if score < 40:
            strengths = [
                f"Initiative to learn {topic}",
                "Willingness to attempt challenges",
                "Growth mindset",
            ]
            weak_areas = [
                f"Foundational {topic} concepts",
                "Core terminology and definitions",
                f"Practical application of {topic}",
            ]
            level = "Beginner"
        elif score < 60:
            strengths = [
                f"Basic understanding of {topic}",
                "Ability to identify key concepts",
                f"Some practical {topic} awareness",
            ]
            weak_areas = [
                f"Deeper {topic} principles",
                "Complex problem-solving",
                "Advanced use cases",
            ]
            level = "Beginner"
        elif score < 75:
            strengths = [
                f"Solid {topic} foundation",
                "Good problem-solving skills",
                f"Applied knowledge of {topic}",
            ]
            weak_areas = [
                f"Advanced {topic} techniques",
                "Optimization strategies",
                "Edge case handling",
            ]
            level = "Intermediate"
        elif score < 90:
            strengths = [
                f"Strong {topic} expertise",
                "Advanced problem-solving ability",
                "Nuanced understanding",
            ]
            weak_areas = [
                f"Specialized {topic} domains",
                "Cutting-edge techniques",
                f"{topic} performance optimization",
            ]
            level = "Advanced"
        else:
            strengths = [
                f"Expert-level {topic} knowledge",
                "Exceptional problem-solving skills",
                f"Mastery of complex {topic} concepts",
            ]
            weak_areas = [
                f"Niche {topic} specializations",
                f"Emerging {topic} technologies",
            ]
            level = "Advanced"

        response_text = json.dumps(
            {
                "score": score,
                "strengths": strengths,
                "weak_areas": weak_areas,
                "level": level,
            }
        )
        return [{"generated_text": response_text}]

    elif "Analyze the learner's performance" in prompt:
        # Performance analysis - pointwise feedback on answers
        topic = "the topic"
        topic_match = re.search(r"TOPIC_IDENTIFIER: ([^\n]+)", prompt)
        if topic_match:
            topic = topic_match.group(1).strip()

        # Extract score from prompt
        score = 50
        score_match = re.search(r"Score: (\d+)", prompt)
        if score_match:
            score = int(score_match.group(1))

        # Extract questions from prompt
        json_match = re.search(r"\[\s*\{.*?\}\s*\]", prompt, re.DOTALL)
        questions_data = []
        if json_match:
            try:
                questions_data = json.loads(json_match.group())
            except:
                questions_data = []

        # Build pointwise analysis
        analysis_sections = []
        correct_count = 0

        if questions_data:
            analysis_sections.append(f"## Performance Analysis for {topic}")
            analysis_sections.append(f"### Overall Score: {score}%\n")
            analysis_sections.append("### Question-by-Question Breakdown:\n")

            for idx, q in enumerate(questions_data, 1):
                student_ans = q.get("student_answer", "").lower().strip()
                correct_ans = q.get("correct_answer", "").lower().strip()
                is_correct = student_ans == correct_ans or correct_ans in student_ans

                if is_correct:
                    correct_count += 1
                    status = "✓ CORRECT"
                else:
                    status = "✗ INCORRECT"

                analysis_sections.append(
                    f"**Question {idx}**: {q.get('question', 'N/A')}"
                )
                analysis_sections.append(
                    f"- Your Answer: {q.get('student_answer', 'No answer')}"
                )
                analysis_sections.append(
                    f"- Correct Answer: {q.get('correct_answer', 'N/A')}"
                )
                analysis_sections.append(f"- Status: {status}")
                analysis_sections.append(
                    f"- Explanation: In {topic}, {correct_ans} is correct because it represents a key concept. Your answer shows understanding of {'the core concept' if is_correct else 'an adjacent area that needs clarification'}."
                )
                analysis_sections.append("")

        # Add summary
        analysis_sections.append("### Summary of Strengths:")
        if correct_count >= 4:
            analysis_sections.append(
                f"- Strong grasp of {topic} fundamentals ({correct_count}/5 correct)"
            )
            analysis_sections.append(
                f"- Demonstrated ability to apply {topic} concepts"
            )
            analysis_sections.append(
                f"- Ready to progress to more advanced {topic} topics"
            )
        elif correct_count >= 2:
            analysis_sections.append(
                f"- Reasonable understanding of {topic} basics ({correct_count}/5 correct)"
            )
            analysis_sections.append(f"- Showing progress in {topic} comprehension")
            analysis_sections.append(f"- Some areas of {topic} need reinforcement")
        else:
            analysis_sections.append(
                f"- Foundation building phase in {topic} ({correct_count}/5 correct)"
            )
            analysis_sections.append(f"- Important to review {topic} fundamentals")
            analysis_sections.append(
                f"- Consistent practice with {topic} concepts will help"
            )

        analysis_sections.append("\n### Areas for Improvement:")
        analysis_sections.append(f"- Focus on the {topic} concepts you got wrong")
        analysis_sections.append(f"- Review {topic} documentation and best practices")
        analysis_sections.append(f"- Practice {topic}-related problems regularly")

        return [{"generated_text": "\n".join(analysis_sections)}]

    elif "Provide detailed explanations of the correct answers" in prompt:
        # Solution explanation - explain answers for each question
        topic = "the topic"
        topic_match = re.search(r"TOPIC_IDENTIFIER: ([^\n]+)", prompt)
        if topic_match:
            topic = topic_match.group(1).strip()

        # Extract score from prompt
        score = 75
        score_match = re.search(r"Score: (\d+)", prompt)
        if score_match:
            score = int(score_match.group(1))

        # Extract questions from prompt
        json_match = re.search(r"\[\s*\{.*?\}\s*\]", prompt, re.DOTALL)
        questions_data = []
        if json_match:
            try:
                questions_data = json.loads(json_match.group())
            except:
                questions_data = []

        # Build solution guide
        solution_sections = []
        solution_sections.append(f"## Solution Guide for {topic}\n")
        solution_sections.append(f"### Detailed Explanation of Correct Answers\n")

        if questions_data:
            for idx, q in enumerate(questions_data, 1):
                correct_ans = q.get("correct_answer", "N/A").strip()
                question_text = q.get("question", "N/A")

                solution_sections.append(f"### Question {idx}: {question_text}\n")
                solution_sections.append(f"**Correct Answer**: {correct_ans}\n")
                solution_sections.append(
                    f"**Explanation**: In {topic}, {correct_ans} is the correct choice because:"
                )
                solution_sections.append(
                    f"- It represents a fundamental principle in {topic}"
                )
                solution_sections.append(
                    f"- It is supported by {topic} best practices and standards"
                )
                solution_sections.append(
                    f"- It demonstrates proper understanding of {topic} concepts"
                )
                solution_sections.append(
                    f"- In practical {topic} applications, this approach is preferred\n"
                )

        solution_sections.append("### Key Takeaways")
        solution_sections.append(f"- These answers reflect core {topic} knowledge")
        solution_sections.append(
            f"- Understanding these concepts is essential for {topic} mastery"
        )
        solution_sections.append(f"- Apply these principles in your {topic} projects")

        return [{"generated_text": "\n".join(solution_sections)}]

    elif "Generate advanced challenge problems" in prompt:
        # Advanced challenges - topic-aware and score-based
        topic = "the topic"
        topic_match = re.search(r"Topic: ([^\n]+)", prompt)
        if topic_match:
            topic = topic_match.group(1).strip()

        # Extract score from prompt for contextual challenges
        score = 75
        score_match = re.search(r"Score: (\d+)", prompt)
        if score_match:
            score = int(score_match.group(1))

        # Adjust challenge difficulty based on score
        if score >= 80:
            challenge_intro = (
                "You've demonstrated strong mastery. Here are expert-level challenges:"
            )
            challenge_level = "expert-level"
            challenges = f"""1. Design a production-grade system using {topic} with millions of concurrent users
2. Implement advanced optimization techniques with measurable performance improvements
3. Architect a scalable solution handling edge cases and failure scenarios
4. Create a solution combining {topic} with other advanced technologies"""
        else:
            challenge_intro = "You're ready for advanced challenges. Here are scenarios to stretch your skills:"
            challenge_level = "advanced"
            challenges = f"""1. Build an optimized solution for a complex {topic} problem
2. Handle multiple edge cases and error conditions gracefully
3. Design a solution that considers scalability and performance
4. Integrate {topic} with complementary technologies or patterns"""

        return [{"generated_text": f"""## Advanced Challenge Problems for {topic}

### {challenge_intro}

### Complex Problem-Solving Challenges
{challenges}

### Real-World Scenarios You'll Encounter
- **Challenge 1**: Design a system where {topic} is critical for performance
- **Challenge 2**: Optimize an existing {topic} implementation for better efficiency
- **Challenge 3**: Build a feature that requires deep {topic} knowledge
- **Challenge 4**: Debug and fix a complex issue involving {topic}

### Architecture & Design Questions
1. What are the trade-offs between different {topic} approaches?
2. How does your {topic} solution scale as complexity increases?
3. What are the security and performance implications of your design?
4. How would you monitor and optimize {topic} usage in production?

### Recommended {challenge_level.title()} Projects
1. Build a complete system showcasing {topic} best practices
2. Optimize an existing solution for performance and maintainability
3. Extend with advanced features and edge case handling
4. Document architecture decisions and trade-offs

### Technical Depth Areas
- Understanding time and space complexity implications
- Caching, memory management, and optimization strategies
- Concurrency and parallel processing with {topic}
- Security considerations and best practice patterns
- Production deployment and monitoring strategies
"""}]

    else:
        # Roadmap - topic, level, and score aware
        topic = "the topic"
        topic_match = re.search(r"Topic: ([^\n]+)", prompt)
        if topic_match:
            topic = topic_match.group(1).strip()

        # Extract target level from prompt
        level = "Advanced"
        if "target level: intermediate" in prompt.lower():
            level = "Intermediate"
        elif "target level: advanced" in prompt.lower():
            level = "Advanced"
        elif "target level: expert" in prompt.lower():
            level = "Expert"

        # Extract score for personalized recommendations
        score = 50
        score_match = re.search(r"Score: (\d+)", prompt)
        if score_match:
            score = int(score_match.group(1))

        # Determine roadmap specifics based on target level
        if level == "Intermediate":
            duration = "30-Day"
            intro = f"This {duration} roadmap will help you progress from {topic} fundamentals to intermediate-level proficiency with practical {topic} applications."
            week_topics = [
                (
                    "Core {topic} Patterns",
                    f"- Mastering {topic} design patterns and best practices\n- Understanding performance implications in {topic}\n- Real-world {topic} use cases and patterns",
                ),
                (
                    "Practical {topic} Projects",
                    f"- Build a substantial {topic} project from scratch\n- Implement {topic} optimizations and improvements\n- Code review and refactoring exercises with {topic}",
                ),
                (
                    "{topic} Ecosystem & Tools",
                    f"- Explore {topic} frameworks and libraries\n- Learn industry-standard {topic} tools\n- Integration of {topic} with complementary technologies",
                ),
                (
                    "Intermediate Problem Solving",
                    f"- Solve medium-complexity {topic} challenges\n- Handle edge cases in {topic} applications\n- Performance tuning and optimization in {topic}",
                ),
            ]
        elif level == "Advanced":
            duration = "30-Day"
            intro = f"This {duration} roadmap will elevate your {topic} skills to advanced level, covering architecture, optimization, and specialization in {topic}."
            week_topics = [
                (
                    "Advanced {topic} Architecture",
                    f"- Design scalable {topic} systems\n- Architectural patterns in {topic}\n- Performance optimization techniques for {topic}",
                ),
                (
                    "Complex {topic} Projects",
                    f"- Build production-grade {topic} systems\n- Handle concurrency and scaling in {topic}\n- Implement advanced {topic} features",
                ),
                (
                    "{topic} Performance & Security",
                    f"- Deep dive into {topic} performance profiling\n- Security best practices in {topic}\n- Optimization and benchmarking in {topic}",
                ),
                (
                    "Mastery & Leadership in {topic}",
                    f"- Contribute to {topic} open source\n- Mentor others in {topic}\n- Explore cutting-edge {topic} innovations",
                ),
            ]
        else:  # Expert
            duration = "30-Day"
            intro = f"This {duration} roadmap guides your journey to {topic} expertise with focus on innovation, contribution, and specialized domains."
            week_topics = [
                (
                    "Expert-Level {topic} Design",
                    f"- Architect systems at scale using {topic}\n- Advanced {topic} optimization techniques\n- Specialized {topic} domains and use cases",
                ),
                (
                    "Innovation in {topic}",
                    f"- Research advanced {topic} techniques\n- Contributing to {topic} ecosystem\n- Building next-generation {topic} solutions",
                ),
                (
                    "{topic} Leadership & Knowledge",
                    f"- Mentor and lead {topic} teams\n- Establish {topic} best practices\n- Share expertise through {topic} content",
                ),
                (
                    "Continuous {topic} Excellence",
                    f"- Stay current with {topic} trends\n- Advanced specialization in {topic}\n- Build your {topic} portfolio projects",
                ),
            ]

        weeks_content = []
        for week_num, (topic_focus, activities) in enumerate(week_topics, 1):
            weeks_content.append(
                f"### Week {week_num}: {topic_focus.format(topic=topic)}"
            )
            weeks_content.append(activities.format(topic=topic))
            weeks_content.append("")

        return [
            {
                "generated_text": f"""## {duration} Personalized Learning Roadmap for {topic} ({level} Level)

{intro}

**Assessment Score**: {score}% | **Target Level**: {level}

### Learning Strategy
- **Daily Time Commitment**: 2-3 hours of focused {topic} learning
- **Approach**: Build real projects while learning {topic} concepts
- **Assessment**: Weekly {topic} challenges to track progress
- **Outcome**: Master {topic} at {level} level

### Month-Long Structure

{chr(10).join(weeks_content)}

### {topic}-Specific Technical Focus Areas
**Core Competencies to Develop**:
- Advanced {topic} patterns and idioms
- {topic} performance optimization and profiling
- Scalable {topic} architecture
- {topic} best practices and standards
- Integration of {topic} with related technologies

### Hands-On Projects for {topic}
- Project 1: Build a substantial application using {topic}
- Project 2: Optimize and scale an existing {topic} system
- Project 3: Contribute to {topic} open source
- Project 4: Create a specialized {topic} solution

### Daily {topic} Practice Schedule
- 45 minutes: Study {topic} concepts and patterns
- 60 minutes: Hands-on {topic} coding and projects
- 30 minutes: {topic} problem-solving and challenges
- 15 minutes: Review, refactor, and document {topic} work

### Resources for {topic} Mastery
- Official {topic} documentation and guides
- {topic}-specific books and advanced courses
- {topic} community forums and discussions
- {topic} open source repositories and contributions

### Success Indicators
- Proficiency in complex {topic} problem-solving
- Ability to architect {topic} solutions at scale
- Understanding of {topic} internals and optimization
- Recognition as a {topic} expert in your network

### Continuous Growth in {topic}
1. Master current {topic} version and features
2. Explore {topic} ecosystem tools and libraries
3. Contribute to {topic} community
4. Specialize in {topic} subdomain
5. Mentor others in {topic}
"""
            }
        ]
