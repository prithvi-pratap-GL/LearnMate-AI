# LearnMate AI Test Cases

This document outlines the test cases for the LearnMate AI application, covering frontend, backend, AI workflow, and error handling.

## 1. Frontend Validation Tests

-   **Test Case 1.1: Submit form with empty topic.**
    -   **Action**: User clicks "Analyze" without entering a topic.
    -   **Expected Result**: A validation message appears under the topic field, e.g., "Topic is required." The API call is not made.

-   **Test Case 1.2: Submit form with no questions.**
    -   **Action**: User fills out the topic but does not add any questions.
    -   **Expected Result**: A validation message appears, e.g., "At least one question is required." The API call is not made.

-   **Test Case 1.3: Submit form with an empty student answer.**
    -   **Action**: User adds a question but leaves the student answer field blank.
    -   **Expected Result**: A validation message appears for the empty field. The API call is not made.

-   **Test Case 1.4: Dynamic question fields.**
    -   **Action**: User clicks "Add Question" button.
    -   **Expected Result**: A new set of input fields for a question appears.
    -   **Action**: User clicks "Remove" button on a question.
    -   **Expected Result**: The corresponding question's input fields are removed.

## 2. Backend API Tests

-   **Test Case 2.1: Valid request to `/analyze-learning`.**
    -   **Action**: Send a POST request with a valid JSON payload.
    -   **Expected Result**: The API returns a `200 OK` status code and a JSON response containing the analysis.

-   **Test Case 2.2: Request with empty topic.**
    -   **Action**: Send a POST request with `topic` set to `""`.
    -   **Expected Result**: The API returns a `422 Unprocessable Entity` validation error.

-   **Test Case 2.3: Request with empty questions list.**
    -   **Action**: Send a POST request with `questions` as an empty array `[]`.
    -   **Expected Result**: The API returns a `422 Unprocessable Entity` validation error.

-   **Test Case 2.4: Malformed JSON payload.**
    -   **Action**: Send a POST request with a malformed JSON body.
    -   **Expected Result**: The API returns a `400 Bad Request` error.

## 3. AI Workflow Tests

-   **Test Case 3.1: Score below 50.**
    -   **Action**: Submit a quiz where the student's answers are mostly incorrect, resulting in a score less than 50.
    -   **Expected Result**: The `generated_content` in the API response contains a `beginner_explanation`.

-   **Test Case 3.2: Score of 50 or above.**
    -   **Action**: Submit a quiz where the student's answers are mostly correct, resulting in a score of 50 or more.
    -   **Expected Result**: The `generated_content` in the API response contains `advanced_challenges`.

-   **Test Case 3.3: LLM returns invalid JSON for evaluation.**
    -   **Action**: Mock the Hugging Face API to return a non-JSON string for the first evaluation call.
    -   **Expected Result**: The backend should catch the JSON decoding error and return a `500 Internal Server Error` with a user-friendly message.

-   **Test Case 3.4: All three LLM calls are executed.**
    -   **Action**: Submit a valid quiz.
    -   **Expected Result**: The backend should successfully execute all three LLM calls (evaluation, content generation, roadmap) and return a complete response.

## 4. Error Handling Tests

-   **Test Case 4.1: Hugging Face API is unavailable.**
    -   **Action**: Mock the Hugging Face API to be unreachable (e.g., return a 503 Service Unavailable error).
    -   **Expected Result**:
        -   **Backend**: Returns a `500 Internal Server Error` with a message like "AI service is currently unavailable."
        -   **Frontend**: Displays a user-friendly error message on the dashboard, e.g., "Failed to get AI analysis. Please try again later."

-   **Test Case 4.2: Hugging Face API times out.**
    -   **Action**: Mock the Hugging Face API to have a long delay, causing the request to time out.
    -   **Expected Result**:
        -   **Backend**: Returns a `500 Internal Server Error` indicating a timeout.
        -   **Frontend**: Displays a timeout error message.

-   **Test Case 4.3: Invalid Hugging Face API Key.**
    -   **Action**: Use an invalid API key in the `.env` file.
    -   **Expected Result**:
        -   **Backend**: Returns a `500 Internal Server Error` (or a more specific error if possible) indicating an authentication issue with the AI service.
        -   **Frontend**: Displays a generic error message.
