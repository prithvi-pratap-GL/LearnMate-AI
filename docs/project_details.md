
# Project Details: LearnMate AI

## Project Purpose

LearnMate AI is an intelligent, two-round adaptive learning assessment platform. It's designed to dynamically evaluate a user's understanding of a specific topic, provide detailed feedback on their answers, and generate a personalized, structured learning roadmap to help them improve.

The core feature is a two-round quiz:
- **Round 1:** Beginner-level multiple-choice questions.
- **Round 2:** Advanced-level questions, which are only presented to users who score 50% or higher in Round 1.

Based on the performance, the application provides explanations, highlights strengths and weaknesses, and creates a 30-day learning plan.

## Architecture

The project follows a standard client-server architecture.

### Frontend (Client)

- **Framework:** React with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **Structure:** A single-page application (SPA) with components for the quiz and results dashboard. The main logic is contained within `QuizPage.tsx`.

### Backend (Server)

- **Framework:** FastAPI (Python)
- **Server:** Uvicorn
- **Core Task:** The backend serves a RESTful API that the frontend consumes. Its main responsibilities are:
    - Generating quiz questions of varying difficulty using a Hugging Face language model.
    - Evaluating user submissions.
    - Generating personalized feedback and learning roadmaps using the LLM.
- **Dependencies:** `pydantic` for data validation, `python-dotenv` for managing environment variables.

## How to Start the Project

### Prerequisites

- Python 3.8+ and Pip
- Node.js and npm

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file in the `backend` directory and add your Hugging Face API key:
    ```
    HUGGING_FACE_API_KEY="your_hugging_face_api_key_here"
    ```
4.  Start the server. There are two options:
    - **For development (with auto-reload on port 5000):**
      ```bash
      python run_server.py
      ```
    - **For production (on port 8000):**
      ```bash
      python start.py
      ```

### Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install the required Node.js packages:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
4.  The application will be available at `http://localhost:3000`. It is configured to connect to the backend at `http://localhost:8000`, so you should use the backend's production start script (`python backend/start.py`) for it to work out of the box.

## Environment Variables

The backend requires the following environment variable to be set in a `.env` file in the `backend` directory.

- `HUGGING_FACE_API_KEY`: Your API key for the Hugging Face Inference API. This is used for all LLM calls (question generation, evaluation, etc.).
