def get_learning_generation_prompt(topic: str, user_level: str) -> str:
    """
    Returns the strict system prompt for Llama 3 to generate adaptive learning content.
    """
    level_instructions = {
        "Beginner": "Use highly simple analogies, avoid complex jargon, and explain fundamental concepts clearly as if speaking to a high school student.",
        "Intermediate": "Assume foundational working knowledge. Introduce technical terms along with their practical usage and underlying architecture.",
        "Expert": "Dive extremely deep into internal mechanisms, advanced edge cases, performance trade-offs, and state-of-the-art abstractions."
    }
    
    instruction = level_instructions.get(user_level, level_instructions["Beginner"])

    prompt = f"""You are an expert, adaptive teaching AI system. Your task is to generate highly educational content.
Subject Topic: {topic}
Target Audience Level: {user_level}

ADAPTIVE INSTRUCTION: 
{instruction}

OUTPUT RULES:
1. You MUST respond with ONLY a valid, raw JSON object.
2. DO NOT output any conversational text, markdown formatting (no ```json code blocks), or explanations outside of the JSON structure.
3. Ensure the JSON is strictly formatted and keys are double-quoted.

JSON STRUCTURE MATCHING EXACTLY:
{{
  "explanation": "A comprehensive 3-5 sentence explanation adapted deeply to the {user_level} level.",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "examples": "One clear, concrete real-world professional example demonstrating the topic.",
  "mcqs": [
    {{
      "question": "A multiple choice question testing {user_level} knowledge on {topic}",
      "options": ["A or option 1", "B or option 2", "C or option 3", "D or option 4"],
      "answer": "The exact string matching the correct option from the options list"
    }}
  ]
}}
"""
    return prompt.strip()

def get_quiz_generation_prompt(
    topic: str,
    difficulty: str,
    correct_streak: int = 0,
    wrong_streak: int = 0,
    last_correct: bool = False,
    n: int = 2
) -> str:
    """
    Returns the adaptive quiz prompt with streak-only difficulty logic.
    Generates exactly `n` questions per request (default 2).
    """

    prompt = f"""You are an AI-powered quiz question generator for an Adaptive Quiz System.

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
"""
    return prompt.strip()
