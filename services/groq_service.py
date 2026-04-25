import os
import logging
from dotenv import load_dotenv
from typing import Optional

# Setup logging
logger = logging.getLogger(__name__)

# Robust Groq Import
try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.error("Groq library not installed. Please run 'pip install groq'.")

# Load .env variables proactively if they exist
load_dotenv()

# Model Configuration
MODEL_CONFIG = {
    "default": "llama-3.1-8b-instant",
    "high_quality": "llama-3.3-70b-versatile",
    "backup": "openai/gpt-oss-20b",
    "fast": "llama-3.1-8b-instant"
}

# Core Groq Service Class
class GroqService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Groq client.
        Uses GROQ_API_KEY from environment variables by default.
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not GROQ_AVAILABLE:
            logger.error("CRITICAL: Groq library is not installed.")
            self.client = None
        elif not self.api_key:
            logger.error("CRITICAL: GROQ_API_KEY not found in environment variables.")
            self.client = None
        else:
            self.client = AsyncGroq(api_key=self.api_key)

    def _get_model(self, model: Optional[str] = None, task: Optional[str] = None) -> str:
        """
        Helper to determine the model based on the provided model name or task.
        """
        if model:
            return model
        
        if task == "quiz":
            return MODEL_CONFIG["fast"]
        elif task == "learning":
            return MODEL_CONFIG["high_quality"]
        
        return MODEL_CONFIG["default"]

    async def generate_response(
        self, 
        prompt: str, 
        system_message: str = "You are a helpful assistant.", 
        temperature: float = 0.7,
        model: Optional[str] = None,
        task: Optional[str] = None
    ) -> str:
        """
        Calls Groq API to generate a response for a given prompt.
        Supports dynamic model selection via 'model' or 'task'.
        """
        if not GROQ_AVAILABLE:
            raise RuntimeError("Groq library is not installed. Cloud fallback unavailable.")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not configured. Cannot process cloud pipeline request.")

        selected_model = self._get_model(model=model, task=task)
        logger.info(f"Using model: {selected_model} for task: {task}")

        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_message,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=selected_model,
                temperature=temperature,
            )
            return chat_completion.choices[0].message.content or ""
        
        except Exception as e:
            logger.error(f"Groq API Error: {str(e)}")
            # Optional: Fallback to backup model if primary fails
            if selected_model != MODEL_CONFIG["backup"]:
                logger.info(f"Retrying with backup model: {MODEL_CONFIG['backup']}")
                return await self.generate_response(
                    prompt=prompt, 
                    system_message=system_message, 
                    temperature=temperature, 
                    model=MODEL_CONFIG["backup"]
                )
            raise RuntimeError(f"Groq generation failed cleanly: {str(e)}")

    async def stream_response(
        self, 
        prompt: str, 
        system_message: str = "You are a helpful assistant.", 
        temperature: float = 0.7,
        model: Optional[str] = None,
        task: Optional[str] = None
    ):
        """
        Calls Groq API to generate a streaming response for a given prompt.
        Supports dynamic model selection via 'model' or 'task'.
        """
        if not GROQ_AVAILABLE:
            raise RuntimeError("Groq library is not installed. Cloud fallback unavailable.")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not configured. Cannot process cloud pipeline request.")

        selected_model = self._get_model(model=model, task=task)
        logger.info(f"Using model: {selected_model} for task: {task} (Stream)")

        try:
            stream = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_message,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=selected_model,
                temperature=temperature,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            logger.error(f"Groq API Stream Error: {str(e)}")
            if selected_model != MODEL_CONFIG["backup"]:
                logger.info(f"Retrying stream with backup model: {MODEL_CONFIG['backup']}")
                async for chunk in self.stream_response(
                    prompt=prompt, 
                    system_message=system_message, 
                    temperature=temperature, 
                    model=MODEL_CONFIG["backup"]
                ):
                    yield chunk
            else:
                raise RuntimeError(f"Groq stream generation failed: {str(e)}")

# Reusable Instance
groq_service = GroqService()


# Example Usage (Public Utility Function)
async def call_groq_api(
    prompt: str, 
    system_message: str = "You are an AI Teacher.", 
    model: Optional[str] = None,
    task: Optional[str] = None
) -> str:
    """
    Clean wrapper function for external calls with dynamic model support.
    """
    return await groq_service.generate_response(prompt, system_message, model=model, task=task)

async def call_groq_api_stream(
    prompt: str, 
    system_message: str = "You are an AI Teacher.", 
    model: Optional[str] = None,
    task: Optional[str] = None
):
    """
    Clean wrapper function for external streaming calls with dynamic model support.
    """
    async for chunk in groq_service.stream_response(prompt, system_message, model=model, task=task):
        yield chunk
