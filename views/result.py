import streamlit as st
from views.styles import inject_global_css

def _diff_display(d):
    c, t = d["correct"], d["total"]
    if t == 0: return "—", "No data"
    return f"{c}/{t}", f"{int(c/t*100)}%"

def render():
    inject_global_css()
    st.markdown("""
<style>
.result-hero {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 3rem 2rem 2.5rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    margin-bottom: 1.75rem;
}
.result-score {
    font-size: 5.5rem;
    font-weight: 900;
    color: #8450B3;
    line-height: 1;
    text-shadow: 0 4px 20px rgba(132,80,179,0.4);
}
.result-score sub { font-size: 2rem; font-weight: 500; color: rgba(255,255,255,0.4); text-shadow: none; }
.result-acc { font-size: 1rem; color: rgba(255,255,255,0.65); margin-top: 0.5rem; }

.diff-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin-bottom:1.5rem; }
.diff-card {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 14px;
    padding: 1.3rem;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}
.diff-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.4rem; }
.diff-score { font-size: 1.6rem; font-weight: 800; color: #FFFFFF; }
.diff-pct   { font-size: 0.82rem; margin-top: 0.2rem; opacity: 0.8; }

.diff-easy   { border-color: rgba(78, 190, 123, 0.3); background: rgba(78, 190, 123, 0.1); }
.diff-easy   .diff-label, .diff-easy   .diff-score, .diff-easy   .diff-pct { color:#4EBE7B; }
.diff-medium { border-color: rgba(209, 165, 81, 0.3); background: rgba(209, 165, 81, 0.1); }
.diff-medium .diff-label, .diff-medium .diff-score, .diff-medium .diff-pct { color:#D1A551; }
.diff-hard   { border-color: rgba(217, 92, 92, 0.3); background: rgba(217, 92, 92, 0.1); }
.diff-hard   .diff-label, .diff-hard   .diff-score, .diff-hard   .diff-pct { color:#D95C5C; }

.motivation-card {
    background: rgba(132, 80, 179, 0.15);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(132, 80, 179, 0.3);
    border-left: 4px solid #8450B3;
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    font-size: 0.95rem;
    color: #D0B0F4;
    font-style: italic;
    margin-bottom: 1.75rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

    TOTAL = 15
    score       = st.session_state.get("score", 0)
    diff_scores = st.session_state.get("diff_scores", {
        "Easy":{"correct":0,"total":0}, "Medium":{"correct":0,"total":0}, "Hard":{"correct":0,"total":0}
    })
    accuracy = int(score / TOTAL * 100) if TOTAL else 0

    if accuracy <= 40:
        level, badge_cls, motivation = "Beginner",     "badge-beginner",     "Keep going — every expert was once a beginner!"
    elif accuracy <= 70:
        level, badge_cls, motivation = "Intermediate", "badge-intermediate", "Good work! Push a little harder to reach Expert level."
    else:
        level, badge_cls, motivation = "Expert",       "badge-expert",       "Outstanding! You've mastered this domain. 🎉"

    # Hero
    st.markdown(f"""<div class="result-hero">
<span class="als-badge {badge_cls}">{level}</span>
<div class="result-score">{score}<sub>/{TOTAL}</sub></div>
<div class="result-acc">Overall Accuracy &nbsp;·&nbsp; <strong style="color:#FFFFFF">{accuracy}%</strong></div>
</div>""", unsafe_allow_html=True)

    # Difficulty grid
    st.markdown('<div class="als-section-title">Performance by Difficulty</div>', unsafe_allow_html=True)
    def diff_card(label, css, d):
        s, p = _diff_display(d)
        return f"""<div class="diff-card diff-{css}">
<div class="diff-label">{label}</div>
<div class="diff-score">{s}</div>
<div class="diff-pct">{p}</div>
</div>"""

    st.markdown(f"""<div class="diff-grid">
{diff_card("Easy",   "easy",   diff_scores.get("Easy",   {"correct":0,"total":0}))}
{diff_card("Medium", "medium", diff_scores.get("Medium", {"correct":0,"total":0}))}
{diff_card("Hard",   "hard",   diff_scores.get("Hard",   {"correct":0,"total":0}))}
</div>""", unsafe_allow_html=True)

    # Motivation
    st.markdown(f'<div class="motivation-card">💬 &nbsp; "{motivation}"</div>', unsafe_allow_html=True)

    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 View Weak Topics", use_container_width=True):
            st.session_state.page = "Learning"
            st.rerun()
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            for k, v in [("question_num",1),("score",0),("current_question",None),
                         ("diff_scores",{"Easy":{"correct":0,"total":0},"Medium":{"correct":0,"total":0},"Hard":{"correct":0,"total":0}})]:
                st.session_state[k] = v
            st.session_state.page = "Home"
            st.rerun()
