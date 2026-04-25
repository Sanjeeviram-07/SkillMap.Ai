import streamlit as st
import time
from views.styles import inject_global_css, inject_anti_cheating_scripts
import requests

TOTAL_QUESTIONS = 15
API_BASE_URL = "http://localhost:8000"

DIFF_STYLE = {
    "Easy":   {"bg": "rgba(78, 190, 123, 0.15)", "color": "#4EBE7B", "border": "rgba(78, 190, 123, 0.3)"},
    "Medium": {"bg": "rgba(209, 165, 81, 0.15)", "color": "#D1A551", "border": "rgba(209, 165, 81, 0.3)"},
    "Hard":   {"bg": "rgba(217, 92, 92, 0.15)", "color": "#D95C5C", "border": "rgba(217, 92, 92, 0.3)"},
}

def init_state():
    defaults = {
        "question_num": 1,
        "score": 0,
        "current_question": None,
        "question_buffer": [],
        "current_difficulty": "Easy",
        "correct_streak": 0,
        "wrong_streak": 0,
        "last_correct": False,
        "diff_scores": {
            "Easy":   {"correct": 0, "total": 0},
            "Medium": {"correct": 0, "total": 0},
            "Hard":   {"correct": 0, "total": 0},
        },
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def fetch_questions_batch():
    domain = st.session_state.selected_domain
    diff = st.session_state.current_difficulty

    params = {
        "topic": domain,
        "difficulty": diff,
        "correct_streak": st.session_state.correct_streak,
        "wrong_streak": st.session_state.wrong_streak,
        "last_correct": st.session_state.last_correct,
        "n": 2
    }

    try:
        res = requests.get(f"{API_BASE_URL}/generate-questions", params=params, timeout=60)
        res.raise_for_status()
        st.session_state.question_buffer.extend(res.json())
    except Exception as e:
        st.error(f"❌ Error connecting to AI service: {e}")
        st.session_state.question_buffer.append({
            "question": "Fallback question",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A",
            "explanation": "API not working",
            "difficulty": diff,
            "topic": domain
        })


def render():
    inject_global_css()
    inject_anti_cheating_scripts()
    
    st.markdown("""
<style>
.quiz-card {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    margin-bottom: 1.25rem;
}
.quiz-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.25rem;
}
.quiz-q-num {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: rgba(255,255,255,0.65);
}
.diff-pill {
    display: inline-block;
    font-size: 0.73rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    border: 1px solid;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.quiz-question {
    font-size: 1.3rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.5;
    margin-bottom: 0.25rem;
}
.stat-row {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
}
.stat-chip {
    flex: 1;
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 0.85rem;
    text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}
.stat-val   { font-size: 1.3rem; font-weight: 800; color: #FFFFFF; }
.stat-label { font-size: 0.7rem; color: rgba(255,255,255,0.65); text-transform: uppercase; letter-spacing: 1px; margin-top: 0.1rem; }
.explanation-box {
    margin-top: 1rem;
    padding: 1.25rem;
    background: rgba(132, 80, 179, 0.15);
    backdrop-filter: blur(12px);
    border-left: 4px solid #8450B3;
    border-radius: 8px;
    color: #FFFFFF;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)
    
    init_state()

    # Domain guard (OLD UI)
    if not st.session_state.get("domain_confirmed", False):
        st.markdown("""
<div style="display:flex;justify-content:center;align-items:center;min-height:50vh;">
  <div style="background:rgba(255,255,255,0.04);backdrop-filter:blur(12px);
              border:1px solid rgba(255,255,255,0.08);border-radius:16px;
              padding:2.5rem 3rem;text-align:center;max-width:480px;
              box-shadow:0 8px 32px rgba(0,0,0,0.3);">
    <div style="font-size:2.5rem;margin-bottom:0.75rem;">⚠️</div>
    <div style="font-size:1.15rem;font-weight:700;color:#FFFFFF;margin-bottom:0.4rem;">
      Please choose a domain first to start the quiz.
    </div>
  </div>
</div>""", unsafe_allow_html=True)
        st.stop()

    domain = st.session_state.selected_domain
    q_num = st.session_state.question_num

    if q_num > TOTAL_QUESTIONS:
        st.session_state.page = "Result"
        st.rerun()
        return

    # Fetch question
    if not st.session_state.current_question:
        if not st.session_state.question_buffer:
            with st.spinner("🧠 Generating adaptive questions..."):
                fetch_questions_batch()

        st.session_state.current_question = st.session_state.question_buffer.pop(0)

    q = st.session_state.current_question

    # 🔹 ONLY FOR DISPLAY (IMPORTANT FIX)
    raw_diff = q.get("difficulty", "Easy")
    if raw_diff not in ["Easy", "Medium", "Hard"]:
        raw_diff = "Medium"

    display_diff = raw_diff
    ds = DIFF_STYLE.get(display_diff, DIFF_STYLE["Medium"])

    # Progress
    st.progress(q_num / TOTAL_QUESTIONS)

    # OLD UI CARD
    st.markdown(f"""
    <div class="quiz-card">
        <div class="quiz-meta">
            <span class="quiz-q-num">Question {q_num} of {TOTAL_QUESTIONS} · {domain}</span>
            <span class="diff-pill" style="background:{ds['bg']};color:{ds['color']};border-color:{ds['border']}">
                {display_diff}
            </span>
        </div>
        <div class="quiz-question">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"🚀 Source: {q.get('source', 'AI')}")

    # Options with labels (OLD UI)
    options = q["options"]
    labels = ["A", "B", "C", "D"]
    formatted = [f"{labels[i]}) {options[i]}" for i in range(len(options))]

    selected_option = st.radio("Choose your answer:", formatted, label_visibility="collapsed")

    if st.button("Submit Answer →", use_container_width=True):

        selected_val = selected_option.split(") ", 1)[1]
        correct_val = q["answer"]

        is_correct = selected_val == correct_val
        st.session_state.last_correct = is_correct

        # ───── DIFFICULTY SCORE TRACKING ─────
        st.session_state.diff_scores[display_diff]["total"] += 1

        # ───── STREAK UPDATE ─────
        if is_correct:
            st.success("✅ Correct!")
            st.session_state.score += 1
            st.session_state.diff_scores[display_diff]["correct"] += 1
            st.session_state.correct_streak += 1
            st.session_state.wrong_streak = 0
        else:
            st.error(f"❌ Incorrect — correct answer was: {correct_val}")
            st.session_state.wrong_streak += 1
            st.session_state.correct_streak = 0

        # Explanation (OLD UI STYLE)
        st.markdown(
            f'<div class="explanation-box"><strong>Explanation:</strong> {q.get("explanation","No explanation")}</div>',
            unsafe_allow_html=True
        )

        # 🔥 FIXED ADAPTIVE LOGIC
        level = st.session_state.current_difficulty

        if st.session_state.correct_streak >= 2:
            if level == "Easy":
                level = "Medium"
            elif level == "Medium":
                level = "Hard"

            st.session_state.correct_streak = 0
            st.session_state.wrong_streak = 0

        elif st.session_state.wrong_streak >= 2:
            if level == "Hard":
                level = "Medium"
            elif level == "Medium":
                level = "Easy"

            st.session_state.correct_streak = 0
            st.session_state.wrong_streak = 0

        st.session_state.current_difficulty = level

        time.sleep(2)
        st.session_state.current_question = None
        st.session_state.question_num += 1
        st.rerun()

    # OLD UI STATS
    answered = max(q_num - 1, 1)
    acc = int(st.session_state.score / answered * 100) if q_num > 1 else 0
    st.markdown(f"""<div class="stat-row">
<div class="stat-chip"><div class="stat-val">{st.session_state.score}</div><div class="stat-label">Score</div></div>
<div class="stat-chip"><div class="stat-val">{q_num}/{TOTAL_QUESTIONS}</div><div class="stat-label">Progress</div></div>
<div class="stat-chip"><div class="stat-val">{acc}%</div><div class="stat-label">Accuracy</div></div>
</div>""", unsafe_allow_html=True)