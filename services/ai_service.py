"""
services/ai_service.py
----------------------
AI generation service layer backed by Ollama (llama3).

Exposes two public functions:
  - async generate_learning_content(topic, level) -> LearningContent
  - async generate_quiz(topic, level)             -> list[QuizQuestion]

Both return fully-typed Pydantic models so callers can rely on a
guaranteed schema regardless of what the LLM actually produces.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

import httpx
from pydantic import BaseModel, Field, validator, root_validator

# ── Logging ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ── Ollama Config ─────────────────────────────────────────────────────────────
_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
_OLLAMA_MODEL    = "llama3"
_TIMEOUT_SECONDS = 90.0


# ═══════════════════════════════════════════════════════════════════════════════
# Output Schemas (Pydantic)
# ═══════════════════════════════════════════════════════════════════════════════

class MCQ(BaseModel):
    question: str
    options: list[str] = Field(..., min_items=4, max_items=4)
    answer: str

class SourceLink(BaseModel):
    title: str
    url: str

class LearningContent(BaseModel):
    """Structured output for generate_learning_content() matching the new web-source spec."""
    title: str
    level: str
    explanation: str
    key_points: list[str]
    example: str
    difficulty_note: str
    sources: list[SourceLink] = Field(default_factory=list)

    @validator("key_points", pre=True, each_item=True)
    def strip_bullets(cls, v: str) -> str:
        """Remove leading bullet/dash chars from LLM output."""
        return re.sub(r"^[\-\*\•\d\.]+\s*", "", str(v)).strip()


class QuizQuestion(BaseModel):
    """Structured output for a single quiz question."""
    question: str
    options: list[str] = Field(..., min_items=4, max_items=4)
    answer: str
    explanation: str = ""
    difficulty: str = ""
    topic: str = ""
    source: str = "ai"

    @validator("options", pre=True)
    def handle_dict_options(cls, v):
        if isinstance(v, dict):
            # Convert {"A": "val", "B": "val", ...} to ["val", "val", ...]
            # Ensure we sort by key to maintain A, B, C, D order
            return [v[k] for k in sorted(v.keys()) if k in ["A", "B", "C", "D"]]
        return v

    @validator("answer", pre=True, always=True)
    def handle_correct_answer_field(cls, v, values):
        # If 'answer' is missing but 'correct_answer' exists in the raw data
        # we can't easily see 'correct_answer' here because Pydantic already filtered it
        # So we use a root_validator instead.
        return v

    @root_validator(pre=True)
    def map_correct_answer(cls, values):
        if "correct_answer" in values and "answer" not in values:
            values["answer"] = values["correct_answer"]
        return values

    @validator("answer")
    def answer_must_be_in_options(cls, v: str, values: dict) -> str:
        opts = values.get("options", [])
        if not opts: return v
        
        # If the answer is just 'A', 'B', 'C', or 'D', map it to the option text
        labels = ["A", "B", "C", "D"]
        if v.upper() in labels and len(opts) >= labels.index(v.upper()) + 1:
            return opts[labels.index(v.upper())]

        if v not in opts:
            # Attempt fuzzy fix: pick the best matching option
            for opt in opts:
                if v.lower() in opt.lower() or opt.lower() in v.lower():
                    return opt
            return opts[0]  # Fallback: first option
        return v


# ═══════════════════════════════════════════════════════════════════════════════
# Internal Helpers
# ═══════════════════════════════════════════════════════════════════════════════

async def stream_ollama_async(prompt: str):
    url = f"{_OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": _OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True,
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]

async def generate_with_ollama(prompt: str) -> str:
    """Primary local generation via Ollama."""
    url = f"{_OLLAMA_BASE_URL}/api/generate"
    payload = {"model": _OLLAMA_MODEL, "prompt": prompt, "stream": False}

    # Short 10-second timeout strictly for Ollama fallback mapping
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()

    text = resp.json().get("response", "").strip()
    if not text:
        raise ValueError("Ollama returned an empty response.")
    return text

async def generate_with_groq(prompt: str, task: Optional[str] = None) -> str:
    """Fallback cloud generation via Groq API. Supports task-based model selection."""
    from services.groq_service import call_groq_api
    return await call_groq_api(prompt=prompt, task=task)

async def generate_response(prompt: str, task: Optional[str] = None) -> tuple[Any, str]:
    """
    Unified AI Orchestrator with Retries:
    - Retries up to 2 times if it hits empty text or invalid JSON.
    - Fails over to Groq with task-specific model selection.
    Returns a tuple of (parsed_data, source_provider) where source_provider
    is either "Ollama" or "Groq".
    """
    for attempt in range(2):
        try:
            logger.info("Using Ollama")
            res = await generate_with_ollama(prompt)
            print("https://img.icons8.com/fluency/512/green-circle.png Model used: Ollama (Local)")
            return _extract_json(res), "Ollama"
        except Exception as e:
            logger.warning(f"[AI Router] Ollama attempt {attempt + 1} failed: {str(e)}")

    logger.info(f"Fallback to Groq for task: {task}")
    try:
        res = await generate_with_groq(prompt, task=task)
        print(f"https://img.icons8.com/fluency/512/blue-circle.png Model used: Groq (Cloud) | Task: {task}")
        return _extract_json(res), "Groq"
    except Exception as groq_err:
        logger.error(f"[AI Router] Groq fallback failed: {str(groq_err)}")
        raise RuntimeError(f"CRITICAL: Both Local and Cloud AI Generators failed: {str(groq_err)}")

async def stream_with_groq(prompt: str, task: Optional[str] = None):
    """Fallback cloud streaming generation via Groq API. Supports task-based model selection."""
    from services.groq_service import call_groq_api_stream
    async for chunk in call_groq_api_stream(prompt=prompt, task=task):
        yield chunk

async def stream_unified(prompt: str, task: Optional[str] = None):
    """
    Unified AI Stream Orchestrator:
    - Tries Ollama local stream.
    - If it fails immediately (no chunks yielded), fails over to Groq.
    """
    ollama_ok = False
    try:
        logger.info("Using Ollama for stream")
        async for chunk in stream_ollama_async(prompt):
            ollama_ok = True
            yield chunk
    except Exception as e:
        logger.warning(f"[AI Router Stream] Ollama failed: {str(e)}")

    if not ollama_ok:
        logger.info(f"Fallback to Groq stream for task: {task}")
        try:
            async for chunk in stream_with_groq(prompt, task=task):
                yield chunk
        except Exception as groq_err:
            error_msg = str(groq_err)
            logger.error(f"[AI Router Stream] Groq fallback failed: {error_msg}")
            raise RuntimeError(f"CRITICAL: Both Local and Cloud AI Streaming Generators failed: {error_msg}")

async def generate_text_response(prompt: str, task: Optional[str] = None) -> str:
    """
    Unified AI Orchestrator that returns raw text (Ollama -> Groq fallback).
    """
    for attempt in range(2):
        try:
            logger.info("Using Ollama for text response")
            res = await generate_with_ollama(prompt)
            print("https://img.icons8.com/fluency/512/green-circle.png Model used: Ollama (Local) [Text]")
            return res
        except Exception as e:
            logger.warning(f"[AI Router Text] Ollama attempt {attempt + 1} failed: {str(e)}")

    logger.info(f"Fallback to Groq for text task: {task}")
    try:
        res = await generate_with_groq(prompt, task=task)
        print(f"https://img.icons8.com/fluency/512/blue-circle.png Model used: Groq (Cloud) [Text] | Task: {task}")
        return res
    except Exception as groq_err:
        logger.error(f"[AI Router Text] Groq fallback failed: {str(groq_err)}")
        raise RuntimeError(f"CRITICAL: AI Text Generators failed: {str(groq_err)}")

async def generate_rag_answer(query: str, chunks: list[str]) -> str:
    """
    """
    context = "\n\n".join(chunks)
    prompt = f"""You are an efficient and highly accurate AI assistant.
Use the following Context to answer the Question directly.
If the exact answer is not prominently found in the Context, you MUST reply EXACTLY with the phrase: "Not found in document".
Do NOT use outside knowledge. Keep your response extremely concise and completely accurate.

Context:
{context}

Question:
{query}

Answer:"""
    return await generate_text_response(prompt, task="learning")

def _extract_json(raw: str) -> Any:
    """
    Extracts the first valid JSON object/array from an LLM response.
    Handles code fences, raw JSON, and common malformations.
    """
    # 1. Try code fences first
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", raw, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # 2. Try raw brackets
    for pattern in (r"(\{.*\})", r"(\[.*\])"):
        match = re.search(pattern, raw, re.DOTALL)
        if match:
            try:
                # Clean up common LLM junk like trailing commas or comments
                cleaned = re.sub(r",\s*([\]\}])", r"\1", match.group(1))
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue

    # 3. Last ditch: try to find anything that looks like JSON
    try:
        return json.loads(raw)
    except:
        pass

    raise ValueError(f"No valid JSON found in model output:\n{raw[:300]}")


# ═══════════════════════════════════════════════════════════════════════════════
# Public Service Functions
# ═══════════════════════════════════════════════════════════════════════════════

async def generate_learning_content(topic: str, level: str) -> LearningContent:
    """
    Generate adaptive learning content integrating multiple-choice questions natively.
    """
    prompt = f"""
You are an intelligent learning assistant.

Generate high-quality learning content by combining:
1. Your own AI knowledge
2. Relevant information from reliable web sources

----------------------------------
INPUT
----------------------------------
- Topic: {topic}
- Level: {level}

----------------------------------
CONTENT GENERATION RULES
----------------------------------

1. First, internally gather relevant knowledge about the topic.
2. Enhance the explanation using commonly known reliable sources such as:
   - Educational websites (e.g., Wikipedia, GeeksforGeeks, official docs)
3. Do NOT mention "scraping" or internal process.
4. Provide clean, human-readable learning content.

----------------------------------
LEVEL-BASED INSTRUCTIONS
----------------------------------

If level = Beginner:
- Use very simple language
- Keep explanation short and clear
- Avoid technical jargon
- Use analogies if possible
- Provide only 3-4 key points

----------------------------------

If level = Intermediate:
- Provide clear explanation
- Include real-world examples
- Explain step-by-step
- Add moderate technical depth
- Provide 4-6 key points

----------------------------------

If level = Expert:
- Provide deep and detailed explanation
- Use technical terminology
- Explain underlying mechanisms
- Include advanced insights
- Think like explaining to engineers/scientists
- Provide 6-8 key points

----------------------------------
OUTPUT FORMAT (STRICT JSON)
----------------------------------

{{
  "title": "...",
  "level": "{level}",
  "explanation": "...",
  "key_points": ["...", "..."],
  "example": "...",
  "difficulty_note": "...",
  "sources": [
    {{
      "title": "...",
      "url": "..."
    }}
  ]
}}

----------------------------------
IMPORTANT RULES
----------------------------------

- Return ONLY valid JSON
- Do NOT include markdown or extra text
- Sources must be realistic and relevant
- Keep explanation aligned with level
""".strip()

    logger.info("Generating learning content async | topic=%s level=%s", topic, level)
    data, _source = await generate_response(prompt, task="learning")

    return LearningContent(**data)


async def generate_quiz(topic: str, level: str, num_questions: int = 5) -> list[QuizQuestion]:
    """
    Generate a set of adaptive quiz questions asymptotically.
    """
    difficulty_map = {
        "Beginner":     ["Easy",   "Easy",   "Medium"],
        "Intermediate": ["Easy",   "Medium", "Hard"],
        "Advanced":     ["Medium", "Hard",   "Hard"],
    }
    pool   = difficulty_map.get(level, ["Easy", "Medium", "Hard"])
    diffs  = [pool[i % len(pool)] for i in range(num_questions)]

    prompt = f"""
You are a quiz generator for a {level} learner. Topic: {topic}

Generate exactly {num_questions} multiple-choice questions.
Use this difficulty distribution: {diffs}

Respond ONLY with a valid JSON array (no markdown, no extra text):
[
  {{
    "question": "<clear question text>",
    "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
    "answer": "<exact text of the correct option>",
    "difficulty": "<Easy|Medium|Hard>",
    "explanation": "<one sentence explaining why the answer is correct>"
  }}
]

Rules:
- Exactly 4 options per question.
- "answer" must be the exact string of one of the 4 options.
- Tailor complexity for a {level} learner.
- Do not include any text outside the JSON array.
""".strip()

    logger.info(
        "Generating quiz async | topic=%s level=%s num_questions=%d",
        topic, level, num_questions
    )
    items, _source = await generate_response(prompt, task="quiz")

    if not isinstance(items, list):
        raise ValueError(f"Expected a JSON array for quiz questions, got: {type(items)}")

    questions = [QuizQuestion(**item) for item in items]
    logger.info("Quiz generated: %d questions", len(questions))
    return questions

async def generate_quiz_question(topic: str, difficulty: str) -> QuizQuestion:
    """
    Generate a single, strict-JSON quiz question using the unified fallback layer.
    """
    prompt = f"""
You are an expert quiz question generator.
Topic: {topic}
Difficulty: {difficulty}

Generate exactly ONE multiple-choice question.
Do NOT provide explanations.

Respond ONLY with a valid JSON object in this EXACT schema:
{{
  "question": "<clear question text>",
  "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
  "answer": "<exact string corresponding to the correct option>"
}}
""".strip()

    logger.info("Generating quiz question async | topic=%s difficulty=%s", topic, difficulty)
    data, _source = await generate_response(prompt, task="quiz")

    return QuizQuestion(**data, source=_source)

async def generate_adaptive_questions(
    topic: str,
    difficulty: str,
    correct_streak: int = 0,
    wrong_streak: int = 0,
    last_correct: bool = False,
    n: int = 2
) -> list[QuizQuestion]:
    """
    Generate a batch of strict-JSON quiz questions using streak-based adaptive logic.
    """
    prompt = f"""
You are an AI-powered quiz question generator for an Adaptive Quiz System.

Your task is to generate high-quality multiple-choice questions (MCQs) based ONLY on streak-based adaptive logic.

---

### QUIZ CONFIGURATION:

* Total Questions in Quiz: 15
* Generate Questions Per Request: {n}
* Topic: {topic}
* Current Difficulty Level: {difficulty}

---

### USER PERFORMANCE DATA:

* Correct Streak: {correct_streak}
* Wrong Streak: {wrong_streak}
* Last Answer Correct: {str(last_correct).lower()}

---

### ADAPTIVE LOGIC (STRICT):

1. STREAK RULE:

   * If Correct Streak >= 2 -> Increase difficulty
   * If Wrong Streak >= 2 -> Decrease difficulty

2. DIFFICULTY TRANSITION:

   * Easy -> Medium -> Hard (increase)
   * Hard -> Medium -> Easy (decrease)
   * Do NOT exceed boundaries

3. STABILITY RULE:

   * If no streak condition met -> keep same difficulty

---

### DIFFICULTY DEFINITIONS:

EASY:

* Basic definitions
* Direct recall
* Simple facts

MEDIUM:

* Conceptual understanding
* Moderate reasoning
* Application-based

HARD:

* Scenario-based
* Logical reasoning
* Advanced concepts

---

### INSTRUCTIONS:

1. Determine FINAL difficulty using ONLY streak logic.

2. Generate exactly {n} questions based on FINAL difficulty.

3. Ensure:

   * No duplicate questions
   * Clear wording
   * Balanced options

4. Each question must include:

   * Question
   * 4 options (A, B, C, D)
   * Correct answer
   * Short explanation (1-2 lines)
   * Difficulty
   * Topic

---

### OUTPUT FORMAT (STRICT JSON ONLY):

[
  {{
    "question": "string",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "answer": "The exact string corresponding to the correct option",
    "explanation": "string",
    "difficulty": "{difficulty}",
    "topic": "{topic}"
  }}
]

---

### IMPORTANT:

* Output ONLY valid JSON
* No extra text
* Do NOT mention logic explanation
* Ensure JSON is parseable
""".strip()

    logger.info("Generating adaptive quiz questions async | topic=%s difficulty=%s", topic, difficulty)
    items, source_provider = await generate_response(prompt, task="quiz")

    if not isinstance(items, list):
        raise ValueError(f"Expected a JSON array for quiz questions, got: {type(items)}")

    questions = []
    for item in items:
        item["source"] = source_provider
        questions.append(QuizQuestion(**item))
    return questions

