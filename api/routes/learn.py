from fastapi import APIRouter, Query, HTTPException
import logging
from pydantic import ValidationError

from services.ai_service import generate_learning_content, LearningContent

router = APIRouter(prefix="/learn", tags=["Learning"])
logger = logging.getLogger(__name__)

@router.get("", response_model=LearningContent)
async def get_learning_content(
    topic: str = Query(..., description="The subject or topic to learn about"),
    level: str = Query("Beginner", pattern="^(Beginner|Intermediate|Expert)$", description="User's current mastery level")
):
    """
    Endpoint mapping to /learn?topic={topic}&level={level}
    Generates structured adaptive content and multiple-choice questions natively.
    """
    try:
        # Utilize the dual-engine fallback generator gracefully
        data = await generate_learning_content(topic, level)
        return data

    except ValueError as ve:
        logger.error(f"JSON extraction error in /learn: {str(ve)}")
        raise HTTPException(status_code=502, detail="LLM generated invalid JSON mapping.")
    except ValidationError as val_err:
        logger.error(f"Pydantic schema mismatch in /learn: {str(val_err)}")
        raise HTTPException(status_code=502, detail="LLM output did not match required schema.")
    except Exception as e:
        logger.error(f"Unexpected failover engine crash: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal AI service offline or unreachable.")
