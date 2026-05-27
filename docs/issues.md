
# Identified Project Issues

This document lists potential issues and areas for improvement within the LearnMate AI project.

## 1. Conflicting Backend Server Implementations

- **Issue:** There are three separate Python scripts for running the server: `start.py`, `run_server.py`, and `minimal_server.py`.
- **Details:**
    - `start.py` runs a FastAPI server on port `8000`.
    - `run_server.py` runs a FastAPI server on port `5000` for development.
    - `minimal_server.py` implements a completely separate server using `aiohttp` which duplicates some of the application logic.
- **Impact:** This is confusing for new developers. The presence of `minimal_server.py` suggests either abandoned work or an undocumented alternative, leading to maintenance overhead.
- **Recommendation:** Deprecate and remove `minimal_server.py`. Consolidate `start.py` and `run_server.py` or clarify their roles in the documentation. The port difference between dev and prod for the backend can also cause confusion.


## 2. Missing `.env.example` File

- **Issue:** The project requires a `.env` file for the backend, but there is no example file.
- **Impact:** Developers have to read the source code (`backend/app/config/settings.py`) or the `README.md` to know which environment variables are required.
- **Recommendation:** Add a `.env.example` file to the `backend` directory that lists all required environment variables with placeholder values.

## 3. Suppressed server logs, & degub mode was set to critical

- **Issue:** The server logs were suppressed in the backend, so when you run the server, it doesn't print any logs. The debug mode was set to critical, which suppressed the important logs.
- **Impact:** This can make it difficult to debug issues and understand the behavior of the server.
- **Recommendation:** Enable these logs and set the debug mode to info.

## 4. No guardrails in the question_service.py for the llm output.

- **Issue:** There is no guardrails in the question_service.py for the llm output.
- **Impact:** If the llm output fails, the system will not retry with feedback.
- **RESOLUTION:** AddED guardrails in the question_service.py for the llm output using pydantic. And added a failover mechanism to retry with feedback if the llm output fails.