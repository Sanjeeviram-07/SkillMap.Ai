from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from services.ai_service import stream_unified
import logging

router = APIRouter(prefix="/stream-learn", tags=["Streaming"])
logger = logging.getLogger(__name__)

def get_markdown_prompt(topic: str, level: str) -> str:
    """Prompt strictly asking for Markdown, since streaming raw JSON string fragments breaks UI heavily."""
    return f"""You are an advanced AI teacher.
Topic: {topic}
Level: {level}
Write a beautifully formatted Markdown response covering:
1. Topic explanation (2-3 sentences)
2. 3 to 5 Bullet points with key concepts
3. A real world example

Respond directly with Markdown. Do not wrap in xml or formatting. Make it immediately readable."""

@router.get("")
async def stream_learning_content(
    topic: str = Query(...),
    level: str = Query("Beginner")
):
    """
    Returns an async StreamingResponse yielding Ollama/Groq text chunks dynamically.
    """
    prompt = get_markdown_prompt(topic, level)
    # Return the unbuffered streaming generator natively to the network
    return StreamingResponse(stream_unified(prompt, task="learning"), media_type="text/plain")
