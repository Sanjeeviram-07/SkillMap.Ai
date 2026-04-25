from fastapi import APIRouter, Query, HTTPException
import logging
from pydantic import ValidationError

from services.ai_service import generate_adaptive_questions, QuizQuestion

router = APIRouter(prefix="/generate-questions", tags=["Quiz"])
logger = logging.getLogger(__name__)

@router.get("", response_model=list[QuizQuestion])
async def generate_questions(
    topic: str = Query(..., description="The subject or topic for the quiz question"),
    difficulty: str = Query("Easy", pattern="^(Easy|Medium|Hard)$", description="The difficulty of the question"),
    correct_streak: int = Query(0, description="User's current correct streak"),
    wrong_streak: int = Query(0, description="User's current wrong streak"),
    last_correct: bool = Query(False, description="Whether the last answer was correct"),
    n: int = Query(2, description="Number of questions to generate")
):
    """
    Endpoint mapping to /generate-questions
    Generates a batch of adaptive multiple-choice JSON questions.
    """
    try:
        data = await generate_adaptive_questions(
            topic=topic,
            difficulty=difficulty,
            correct_streak=correct_streak,
            wrong_streak=wrong_streak,
            last_correct=last_correct,
            n=n
        )
        return data

    except ValueError as ve:
        logger.error(f"JSON extraction error in /generate-question: {str(ve)}")
        raise HTTPException(status_code=502, detail="LLM generated invalid JSON mapping.")
    except ValidationError as val_err:
        logger.error(f"Pydantic schema mismatch in /generate-question: {str(val_err)}")
        raise HTTPException(status_code=502, detail="LLM output did not match required schema.")
    except Exception as e:
        logger.error(f"Unexpected failover engine crash: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal AI service offline or unreachable.")
