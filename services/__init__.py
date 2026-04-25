"""
services/
---------
AI service layer for the Adaptive Learning System.

Public API:
    from services.ai_service import generate_learning_content, generate_quiz
    from services.ollama_service import call_ollama
"""
from services.ai_service import generate_learning_content, generate_quiz
from services.ollama_service import call_ollama

__all__ = ["generate_learning_content", "generate_quiz", "call_ollama"]
