import json
from app.services.huggingface_service import query_model, calculate_score_from_answers
from app.utils.prompts import EVALUATION_PROMPT
from app.models.schemas import LearningAnalysisRequest

async def evaluate_learning(request: LearningAnalysisRequest):
    """
    Evaluates the learner's answers using an LLM.
    Calculates score by comparing student answers with correct answers.
    """
    # Calculate score by comparing answers
    questions_list = [
        {
            "question": q.question,
            "student_answer": q.student_answer,
            "correct_answer": q.correct_answer
        }
        for q in request.questions
    ]

    score = calculate_score_from_answers(questions_list)

    # Format answers as JSON for proper parsing in mock response
    answers_json = json.dumps(questions_list)
    answers_str = f"Score: {score}\n\n" + answers_json

    prompt = EVALUATION_PROMPT.format(topic=request.topic, answers=answers_str)

    try:
        response = await query_model(prompt)
        # The response from the model is often a list with one item
        if isinstance(response, list) and len(response) > 0:
            generated_text = response[0].get('generated_text', '{}')
            # Find the last JSON object in the response (to handle case where prompt is repeated)
            json_str_start = generated_text.rfind('{')
            json_str_end = generated_text.rfind('}') + 1
            if json_str_start != -1 and json_str_end > json_str_start:
                json_str = generated_text[json_str_start:json_str_end]
                evaluation_data = json.loads(json_str)
                # Override score with calculated score
                evaluation_data['score'] = score
                return evaluation_data
            else:
                raise ValueError("No JSON object found in the model's response.")
        else:
            raise ValueError("Unexpected response format from the model.")

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON from the model's response: {e}")
    except Exception as e:
        raise e
