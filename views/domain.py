import streamlit as st
from views.styles import inject_global_css

DOMAINS = ["Networking", "AI & ML", "Cloud Computing", "Business Analyst"]
DOMAIN_META = {
    "Networking":       {"icon": "🌐", "desc": "Protocols, OSI model, routing & switching"},
    "AI & ML":          {"icon": "🤖", "desc": "Machine learning, neural networks & data science"},
    "Cloud Computing":  {"icon": "☁️",  "desc": "IaaS, PaaS, SaaS, AWS, Azure & GCP"},
    "Business Analyst": {"icon": "📊", "desc": "KPIs, requirements & stakeholder management"},
}

def render():
    inject_global_css()
    st.markdown("""
<style>
.domain-preview {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-top: 0.75rem;
    margin-bottom: 0.25rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.domain-icon  { font-size: 1.7rem; }
.domain-name  { font-weight: 700; font-size: 1rem; color: #FFFFFF; }
.domain-desc  { font-size: 0.83rem; color: rgba(255,255,255,0.65); margin-top: 0.1rem; }
</style>
""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="als-page-title">Choose Your Domain</div>', unsafe_allow_html=True)
        st.markdown('<div class="als-page-subtitle">Select a knowledge area to start your adaptive learning session.</div>', unsafe_allow_html=True)

        st.markdown('<div class="als-section-title">Available Domains</div>', unsafe_allow_html=True)
        domain = st.selectbox("Domain", DOMAINS, label_visibility="collapsed", key="domain_picker")

        meta = DOMAIN_META.get(domain, {})
        st.markdown(f"""<div class="domain-preview">
<span class="domain-icon">{meta.get('icon','📚')}</span>
<div>
  <div class="domain-name">{domain}</div>
  <div class="domain-desc">{meta.get('desc','')}</div>
</div>
</div>""", unsafe_allow_html=True)

        st.write("")
        if "ready_to_start" not in st.session_state:
            st.session_state["ready_to_start"] = False

        if not st.session_state["ready_to_start"]:
            if st.button("Confirm Selection →", use_container_width=True):
                st.session_state["selected_domain"] = domain
                st.session_state["domain_confirmed"] = True
                st.session_state["ready_to_start"] = True
                # Reset quiz state so a new domain always starts fresh
                for key in ["question_num", "score", "current_question",
                            "question_buffer", "current_difficulty",
                            "correct_streak", "wrong_streak",
                            "response_times", "last_time", "last_correct",
                            "question_start_time", "diff_scores", "answer_log"]:
                    st.session_state.pop(key, None)
                st.rerun()
        else:
            st.success(f"🎯 Domain locked: **{st.session_state['selected_domain']}**")
            st.info("Ready to test your knowledge?")
            if st.button("🚀 Start Quiz", use_container_width=True):
                st.session_state.page = "Quiz"
                # Reset readiness for next time
                st.session_state["ready_to_start"] = False
                st.rerun()
            if st.button("← Change Domain", type="secondary", use_container_width=True):
                st.session_state["ready_to_start"] = False
                st.session_state["domain_confirmed"] = False
                st.rerun()
