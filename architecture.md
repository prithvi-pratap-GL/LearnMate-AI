# LearnMate AI Architecture

## High Level Architecture

The application follows a classic client-server architecture, with a React single-page application (SPA) for the frontend and a Python FastAPI server for the backend.

```
React Frontend (localhost:5173)
       |
       | REST API (Axios)
       v
FastAPI Backend (localhost:8000)
       |
       | AI Workflow Engine
       v
Hugging Face Inference API
```

## Frontend

-   **Framework**: React with Vite for a fast development experience.
-   **Routing**: React Router for managing client-side navigation between pages.
-   **API Communication**: Axios for making REST API calls to the backend.
-   **Styling**: Tailwind CSS for a modern, utility-first CSS workflow. (Optional, but preferred)
-   **UI Components**: The UI is built with responsive components, including a main dashboard, a quiz submission form, and a results display area.

## Backend

The backend is built using FastAPI and is structured to be scalable and maintainable.

-   **Framework**: FastAPI for building high-performance APIs.
-   **Validation**: Pydantic is used for data validation and settings management.
-   **Web Server**: Uvicorn serves as the ASGI server.
-   **CORS**: Middleware is configured to handle Cross-Origin Resource Sharing (CORS) to allow communication from the frontend running on a different port.

### Backend Folder Structure

```
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization and middleware
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── learning.py         # API endpoints for learning analysis
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── huggingface_service.py # Service to interact with Hugging Face API
│   │   ├── evaluation_service.py  # Service for LLM Call 1 (Evaluation)
│   │   ├── challenge_service.py   # Service for LLM Call 2 (Beginner/Advanced)
│   │   └── roadmap_service.py     # Service for LLM Call 3 (Roadmap)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models for request/response validation
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── prompts.py          # Centralized LLM prompts
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── error_handler.py    # Global exception handling middleware
│   │
│   └── config/
│       ├── __init__.py
│       └── settings.py         # Application settings and environment variables
│
├── tests/                      # Unit and integration tests
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables
```

## AI Workflow

The core of the application is the AI workflow, which is orchestrated by the backend.

1.  **LLM Call 1: Evaluation**: The backend receives the student's quiz answers and sends them to the Hugging Face API with a prompt to evaluate the performance. The model is instructed to return a JSON object containing the score, strengths, weak areas, and learning level.

2.  **IF/ELSE Logic**: Based on the `score` returned from the first call:
    -   If the score is less than 50, the backend proceeds to generate a beginner-friendly explanation.
    -   If the score is 50 or greater, the backend proceeds to generate advanced challenge problems.

3.  **LLM Call 2: Content Generation**: A second call is made to the Hugging Face API. The prompt for this call is dynamically chosen based on the `if/else` logic. It will either request a simple explanation or more advanced problems.

4.  **LLM Call 3: Personalized Roadmap**: A final call is made to the Hugging Face API to generate a 30-day personalized learning roadmap, using the context from the previous calls (strengths, weaknesses, level).

This entire workflow is designed to use a maximum of three LLM calls to stay within the project constraints.
