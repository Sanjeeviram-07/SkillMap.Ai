import streamlit as st
import pandas as pd
from views.styles import inject_global_css

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _safe_pct(correct: int, total: int) -> float:
    return round((correct / total) * 100, 1) if total > 0 else 0.0

def _skill_score(score: int, q_answered: int, diff_scores: dict) -> float:
    """
    Weighted skill score 0-1:
      Easy  weight 1, Medium weight 1.5, Hard weight 2
    """
    if q_answered == 0:
        return 0.0
    ds = diff_scores
    weighted_correct = (
        ds["Easy"]["correct"]   * 1.0 +
        ds["Medium"]["correct"] * 1.5 +
        ds["Hard"]["correct"]   * 2.0
    )
    weighted_total = (
        ds["Easy"]["total"]   * 1.0 +
        ds["Medium"]["total"] * 1.5 +
        ds["Hard"]["total"]   * 2.0
    )
    return round(weighted_correct / weighted_total, 3) if weighted_total > 0 else 0.0

def _level_from_skill(skill: float) -> tuple[str, str, str]:
    """Returns (label, badge_color, text_color)"""
    if skill < 0.40:
        return "Beginner", "rgba(217, 92, 92, 0.15)", "#D95C5C"
    elif skill < 0.70:
        return "Intermediate", "rgba(209, 165, 81, 0.15)", "#D1A551"
    else:
        return "Expert", "rgba(78, 190, 123, 0.15)", "#4EBE7B"

def _generate_insights(answer_log: list, diff_scores: dict, response_times: list) -> list[str]:
    """Generate up to 3 dynamic insights from real session data."""
    insights = []
    ds = diff_scores

    # 1. Difficulty comparison
    easy_acc   = _safe_pct(ds["Easy"]["correct"],   ds["Easy"]["total"])
    medium_acc = _safe_pct(ds["Medium"]["correct"], ds["Medium"]["total"])
    hard_acc   = _safe_pct(ds["Hard"]["correct"],   ds["Hard"]["total"])

    if ds["Medium"]["total"] > 0 and ds["Hard"]["total"] > 0:
        if medium_acc > hard_acc:
            insights.append(f"📊 You perform better on **Medium** ({medium_acc:.0f}%) than **Hard** ({hard_acc:.0f}%) questions.")
        elif hard_acc >= medium_acc:
            insights.append(f"🔥 Impressive! You're performing equally well on **Hard** ({hard_acc:.0f}%) and **Medium** ({medium_acc:.0f}%) questions.")
    elif ds["Easy"]["total"] > 0 and ds["Medium"]["total"] > 0:
        if easy_acc > medium_acc:
            insights.append(f"📉 You're stronger on **Easy** ({easy_acc:.0f}%) than **Medium** ({medium_acc:.0f}%). Keep pushing!")
        else:
            insights.append(f"📈 You're rising — stronger on **Medium** ({medium_acc:.0f}%) than **Easy** ({easy_acc:.0f}%).")

    # 2. Response time trend
    if len(response_times) >= 4:
        first_half  = sum(response_times[:len(response_times)//2]) / (len(response_times)//2)
        second_half = sum(response_times[len(response_times)//2:]) / (len(response_times) - len(response_times)//2)
        if second_half < first_half * 0.9:
            insights.append(f"⚡ Your response time is improving — avg dropped from **{first_half:.1f}s** to **{second_half:.1f}s**.")
        elif second_half > first_half * 1.1:
            insights.append(f"🕐 You're spending more time per question lately (**{second_half:.1f}s** vs earlier **{first_half:.1f}s**) — this often means harder questions.")
        else:
            insights.append(f"⏱ Your response time is steady at around **{second_half:.1f}s** per question.")

    # 3. Recent accuracy trend
    if len(answer_log) >= 6:
        last_5  = answer_log[-5:]
        prev_5  = answer_log[-10:-5]
        last_acc = sum(1 for x in last_5 if x["correct"]) / len(last_5) * 100
        if prev_5:
            prev_acc = sum(1 for x in prev_5 if x["correct"]) / len(prev_5) * 100
            if last_acc > prev_acc + 10:
                insights.append(f"🚀 Accuracy jumped from **{prev_acc:.0f}%** to **{last_acc:.0f}%** in the last 5 questions — great momentum!")
            elif last_acc < prev_acc - 10:
                insights.append(f"⚠️ Accuracy dipped from **{prev_acc:.0f}%** to **{last_acc:.0f}%** recently. A short review session may help.")
            else:
                insights.append(f"📌 Your accuracy has been consistent around **{last_acc:.0f}%** in the last 5 questions.")
        else:
            insights.append(f"🎯 Accuracy on the last 5 questions: **{last_acc:.0f}%**.")

    return insights[:3] if insights else ["📋 Complete more questions to unlock personalized insights."]

def _generate_report_markdown(user_name, domain, accuracy, q_answered, skill_pct, diff_scores, level_label, pdf_chat_count, response_times):
    import datetime
    ds = diff_scores
    easy_c, easy_t = ds["Easy"]["correct"], ds["Easy"]["total"]
    med_c, med_t = ds["Medium"]["correct"], ds["Medium"]["total"]
    hard_c, hard_t = ds["Hard"]["correct"], ds["Hard"]["total"]
    
    avg_resp = f"{sum(response_times)/len(response_times):.1f}s" if response_times else "N/A"
    
    # Establish weak areas organically
    weakness_arr = []
    if easy_t > 0 and (easy_c/easy_t) < 0.6: weakness_arr.append("Easy Concepts (High Error Rate)")
    if med_t > 0 and (med_c/med_t) < 0.5: weakness_arr.append("Medium Concepts")
    if hard_t > 0 and (hard_c/hard_t) < 0.4: weakness_arr.append("Advanced Concepts")
    weak_str = "\\n- ".join(weakness_arr) if weakness_arr else "None detected yet."
    
    report = f"""# SkillMap.ai Performance Report
**Generated:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
**User:** {user_name}
**Domain Area:** {domain}

---

## 1. Executive Summary
{user_name} is currently operating at a **{level_label}** proficiency level within the {domain} track. 
Calculated Skill Score stands at **{skill_pct}** across {q_answered} total attempted scenarios.

## 2. Accuracy & Activity Metrics
- **Overall Accuracy**: {accuracy}%
- **Average Response Time**: {avg_resp} per question
- **Total Questions Attempted**: {q_answered}
- **PDF Assistant Inquiries**: {pdf_chat_count} chat interactions logged

### Breakdown by Difficulty
- **Easy**: {easy_c}/{easy_t} correct
- **Medium**: {med_c}/{med_t} correct
- **Hard**: {hard_c}/{hard_t} correct

## 3. Weak Areas Identified
- {weak_str}

## 4. Academic Recommendations
"""
    if "Beginner" in level_label:
        report += "- Focus heavily on understanding the 'Easy' level fundamental concepts before attempting complex questions.\\n- Utilize the PDF Assistant to review core material.\\n"
    elif "Intermediate" in level_label:
        report += "- Your fundamentals are solid. Start heavily integrating Medium questions to push your boundaries.\\n- Review the exact questions you missed in previous sessions.\\n"
    else:
        report += "- You exhibit excellent mastery. Focus purely on Advanced/Hard scenarios to maintain edge.\\n- Help solidify knowledge by uploading complex whitepapers into the PDF Assistant.\\n"

    return report

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────

DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.db-root { font-family: 'Inter', sans-serif; }

/* ── Header ── */
.db-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 1.75rem;
}
.db-domain-title {
    font-size: 2rem;
    font-weight: 900;
    color: #FFFFFF;
    line-height: 1.1;
    margin: 0;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
}
.db-subtitle {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.65);
    margin-top: 0.3rem;
    font-weight: 400;
}
.db-level-badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    border: 1.5px solid;
    margin-top: 0.2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

/* ── KPI Grid ── */
.db-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.db-kpi-card {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.4rem 1.25rem 1.1rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transition: transform 0.15s ease;
}
.db-kpi-card:hover { transform: translateY(-2px); }
.db-kpi-icon { font-size: 1.4rem; margin-bottom: 0.4rem; }
.db-kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1;
}
.db-kpi-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: rgba(255,255,255,0.65);
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-top: 0.45rem;
}

/* ── Section title ── */
.db-section-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: rgba(255,255,255,0.65);
    margin: 1.6rem 0 0.75rem;
}

/* ── Progress ── */
.db-mastery-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.35rem;
}
.db-mastery-label { font-size: 0.85rem; font-weight: 600; color: #FFFFFF; }
.db-mastery-pct   { font-size: 0.85rem; font-weight: 700; color: #8450B3; }

/* ── Diff cards ── */
.db-diff-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 0.5rem;
}
.db-diff-card {
    border-radius: 12px;
    padding: 1.1rem 1rem;
    text-align: center;
    border: 1px solid;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}
.db-diff-name  { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.db-diff-score { font-size: 1.6rem; font-weight: 800; margin: 0.3rem 0 0.1rem; }
.db-diff-sub   { font-size: 0.75rem; font-weight: 500; opacity: 0.8; }

.db-diff-easy   { background:rgba(78, 190, 123, 0.1); border-color:rgba(78, 190, 123, 0.3); }
.db-diff-easy   .db-diff-name, .db-diff-easy .db-diff-score, .db-diff-easy .db-diff-sub { color: #4EBE7B; }

.db-diff-medium { background:rgba(209, 165, 81, 0.1); border-color:rgba(209, 165, 81, 0.3); }
.db-diff-medium .db-diff-name, .db-diff-medium .db-diff-score, .db-diff-medium .db-diff-sub { color: #D1A551; }

.db-diff-hard   { background:rgba(217, 92, 92, 0.1); border-color:rgba(217, 92, 92, 0.3); }
.db-diff-hard   .db-diff-name, .db-diff-hard .db-diff-score, .db-diff-hard .db-diff-sub { color: #D95C5C; }

/* ── Alert cards ── */
.db-alert-card {
    border-radius: 12px;
    padding: 1.15rem 1.4rem;
    margin-bottom: 1.2rem;
    border-left: 4px solid;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}
.db-alert-red    { background:rgba(217, 92, 92, 0.1); border-color:rgba(217, 92, 92, 0.3); border-left-color:#D95C5C; color:#FFFFFF; }
.db-alert-yellow { background:rgba(209, 165, 81, 0.1); border-color:rgba(209, 165, 81, 0.3); border-left-color:#D1A551; color:#FFFFFF; }
.db-alert-green  { background:rgba(78, 190, 123, 0.1); border-color:rgba(78, 190, 123, 0.3); border-left-color:#4EBE7B; color:#FFFFFF; }
.db-alert-title  { font-size: 0.9rem; font-weight: 700; margin-bottom: 0.25rem; }
.db-alert-body   { font-size: 0.84rem; color: rgba(255,255,255,0.7); line-height: 1.55; }

/* ── Insight cards ── */
.db-insight-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.6rem;
    font-size: 0.86rem;
    color: #FFFFFF;
    line-height: 1.5;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}

/* ── No-data state ── */
.db-empty {
    text-align: center;
    padding: 3rem 1rem;
    color: #AFAFBF;
    font-size: 0.9rem;
}
.db-empty-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Main Render
# ─────────────────────────────────────────────────────────────────────────────

def render():
    inject_global_css()
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.markdown('<div class="db-root">', unsafe_allow_html=True)

    # ── Pull session data ────────────────────────────────────────────────────
    domain          = st.session_state.get("selected_domain", "Your Domain")
    score           = st.session_state.get("score", 0)
    question_num    = st.session_state.get("question_num", 1)
    diff_scores     = st.session_state.get("diff_scores", {
        "Easy": {"correct": 0, "total": 0},
        "Medium": {"correct": 0, "total": 0},
        "Hard":   {"correct": 0, "total": 0},
    })
    response_times  = st.session_state.get("response_times", [])
    answer_log      = st.session_state.get("answer_log", [])
    curr_diff       = st.session_state.get("current_difficulty", "Easy")

    q_answered = max(question_num - 1, len(answer_log))
    accuracy   = _safe_pct(score, q_answered)
    skill      = _skill_score(score, q_answered, diff_scores)
    level_label, badge_bg, badge_color = _level_from_skill(skill)
    
    # User Profile Fallback
    user_data = st.session_state.get("user", {})
    user_name = user_data.get("name", "Student")

    # Access PDF Activity
    pdf_log = st.session_state.get("pdf_chat_history", [])
    pdf_chat_count = sum(1 for m in pdf_log if m.get("role") == "user")

    # ── 1. HEADER ────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="db-header">
  <div>
    <div class="db-domain-title">📊 {domain}</div>
    <div class="db-subtitle">Your Performance Overview</div>
    <span class="db-level-badge" style="background:{badge_bg}; color:{badge_color}; border-color:{badge_color}40;">
      {level_label}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── No-data guard ────────────────────────────────────────────────────────
    if q_answered == 0:
        st.markdown("""
<div class="db-empty">
  <div class="db-empty-icon">📋</div>
  <div><strong>No quiz data yet.</strong></div>
  <div>Complete at least one question to see your analytics.</div>
</div>
""", unsafe_allow_html=True)
        if st.button("📝 Start Quiz", use_container_width=True):
            st.session_state.page = "Quiz"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── 2. KPI CARDS ─────────────────────────────────────────────────────────
    st.markdown('<div class="db-section-title">Key Metrics</div>', unsafe_allow_html=True)
    avg_time_str = f"{sum(response_times)/len(response_times):.1f}s" if response_times else "—"
    skill_pct = f"{skill * 100:.0f}%"

    st.markdown(f"""
<div class="db-kpi-grid">
  <div class="db-kpi-card">
    <div class="db-kpi-icon">🎯</div>
    <div class="db-kpi-value">{accuracy:.0f}%</div>
    <div class="db-kpi-label">Accuracy</div>
  </div>
  <div class="db-kpi-card">
    <div class="db-kpi-icon">📝</div>
    <div class="db-kpi-value">{q_answered}</div>
    <div class="db-kpi-label">Questions Attempted</div>
  </div>
  <div class="db-kpi-card">
    <div class="db-kpi-icon">⚡</div>
    <div class="db-kpi-value">{skill_pct}</div>
    <div class="db-kpi-label">Skill Score</div>
  </div>
  <div class="db-kpi-card">
    <div class="db-kpi-icon">🔥</div>
    <div class="db-kpi-value">{curr_diff}</div>
    <div class="db-kpi-label">Current Difficulty</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── 3. MASTERY PROGRESS ───────────────────────────────────────────────────
    st.markdown('<div class="db-section-title">Journey to Mastery</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="db-mastery-row">
  <span class="db-mastery-label">Mastery Progress</span>
  <span class="db-mastery-pct">{skill * 100:.0f}%</span>
</div>
""", unsafe_allow_html=True)
    st.progress(min(skill, 1.0))

    # ── 4. ACCURACY TREND CHART ───────────────────────────────────────────────
    st.markdown('<div class="db-section-title">Accuracy Trend</div>', unsafe_allow_html=True)
    if len(answer_log) >= 2:
        # Rolling cumulative accuracy per question
        cumulative_correct = 0
        chart_data = []
        for i, entry in enumerate(answer_log):
            if entry["correct"]:
                cumulative_correct += 1
            chart_data.append({
                "Question": i + 1,
                "Accuracy (%)": round(cumulative_correct / (i + 1) * 100, 1)
            })
        df_trend = pd.DataFrame(chart_data).set_index("Question")
        st.line_chart(df_trend, use_container_width=True, height=200)
    else:
        st.caption("📈 Answer more questions to see the accuracy trend chart.")

    # ── 5. DIFFICULTY ANALYSIS ────────────────────────────────────────────────
    st.markdown('<div class="db-section-title">Difficulty Breakdown</div>', unsafe_allow_html=True)

    def _diff_display(d: dict) -> tuple[str, str]:
        c, t = d["correct"], d["total"]
        if t == 0:
            return "—", "No data"
        return f"{_safe_pct(c, t):.0f}%", f"{c}/{t} correct"

    easy_val,   easy_sub   = _diff_display(diff_scores["Easy"])
    medium_val, medium_sub = _diff_display(diff_scores["Medium"])
    hard_val,   hard_sub   = _diff_display(diff_scores["Hard"])

    st.markdown(f"""
<div class="db-diff-grid">
  <div class="db-diff-card db-diff-easy">
    <div class="db-diff-name">Easy</div>
    <div class="db-diff-score">{easy_val}</div>
    <div class="db-diff-sub">{easy_sub}</div>
  </div>
  <div class="db-diff-card db-diff-medium">
    <div class="db-diff-name">Medium</div>
    <div class="db-diff-score">{medium_val}</div>
    <div class="db-diff-sub">{medium_sub}</div>
  </div>
  <div class="db-diff-card db-diff-hard">
    <div class="db-diff-name">Hard</div>
    <div class="db-diff-score">{hard_val}</div>
    <div class="db-diff-sub">{hard_sub}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── 6. WEAK AREA DETECTION ────────────────────────────────────────────────
    st.markdown('<div class="db-section-title">Improvement Radar</div>', unsafe_allow_html=True)
    if skill < 0.40:
        css_cls = "db-alert-red"
        icon    = "🔴"
        title   = "⚠️ Improvement Needed"
        body    = (
            f"Your skill score for <strong>{domain}</strong> is <strong>{skill*100:.0f}%</strong>. "
            "You need to strengthen your fundamentals. "
            "Focus on core concepts before attempting harder questions."
        )
    elif skill < 0.70:
        css_cls = "db-alert-yellow"
        icon    = "🟡"
        title   = "📈 You're Making Progress"
        body    = (
            f"You're improving in <strong>{domain}</strong> with a skill score of <strong>{skill*100:.0f}%</strong>. "
            "Keep practicing consistently and aim for more Medium and Hard questions."
        )
    else:
        css_cls = "db-alert-green"
        icon    = "🟢"
        title   = "✅ Strong Performance"
        body    = (
            f"Excellent work in <strong>{domain}</strong>! Your skill score is <strong>{skill*100:.0f}%</strong>. "
            "You're ready to advance to expert-level content."
        )

    st.markdown(f"""
<div class="db-alert-card {css_cls}">
  <div class="db-alert-title">{title}</div>
  <div class="db-alert-body">{body}</div>
</div>
""", unsafe_allow_html=True)

    # ── 7. SMART INSIGHTS ─────────────────────────────────────────────────────
    st.markdown('<div class="db-section-title">Smart Insights</div>', unsafe_allow_html=True)
    insights = _generate_insights(answer_log, diff_scores, response_times)
    for insight in insights:
        st.markdown(f'<div class="db-insight-card">{insight}</div>', unsafe_allow_html=True)

    # ── 8. ACTION BUTTONS ─────────────────────────────────────────────────────
    st.markdown('<div class="db-section-title">Actions</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 Go to Learning", use_container_width=True):
            st.session_state.page = "Learning"
            st.rerun()
    with col2:
        if st.button("📝 Retake Quiz", use_container_width=True):
            # Reset quiz state
            for k, v in [
                ("question_num", 1), ("score", 0),
                ("current_question", None), ("question_buffer", []),
                ("correct_streak", 0), ("wrong_streak", 0),
                ("response_times", []), ("last_time", 0.0),
                ("last_correct", False), ("answer_log", []),
                ("current_difficulty", "Easy"),
                ("diff_scores", {
                    "Easy":   {"correct": 0, "total": 0},
                    "Medium": {"correct": 0, "total": 0},
                    "Hard":   {"correct": 0, "total": 0},
                }),
            ]:
                st.session_state[k] = v
            st.session_state.page = "Quiz"
            st.rerun()

    # ── 9. EXPORT REPORT ──────────────────────────────────────────────────────
    st.markdown('<div class="db-section-title">Documentation</div>', unsafe_allow_html=True)
    report_md = _generate_report_markdown(
        user_name, domain, accuracy, q_answered, skill_pct, 
        diff_scores, level_label, pdf_chat_count, response_times
    )
    
    st.download_button(
        label="📄 Download Performance Report",
        data=report_md,
        file_name=f"{user_name.replace(' ', '_')}_SkillMap_Report.md",
        mime="text/markdown",
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)
