import logging
import streamlit as st
from pydantic import ValidationError
from views.styles import inject_global_css
import requests
from views.eduna_chat import render_eduna_chatbot


logger = logging.getLogger(__name__)

# ── API Connection ─────────────────────────────────────────────────────────────
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

def _fetch_learning_content(domain: str, level: str) -> dict:
    """
    Fetches learning content from the FastAPI backend.
    """
    _LEVEL_MAP = {
        "Beginner Focus":       "Beginner",
        "Intermediate Review":  "Intermediate",
        "Advanced Deep Dive":   "Expert",
    }
    api_level = _LEVEL_MAP.get(level, "Intermediate")
    
    url = f"{API_BASE_URL}/learn"
    try:
        response = requests.get(url, params={"topic": domain, "level": api_level}, timeout=90)
        response.raise_for_status()
        data = response.json()

        return {
            "topic":        data.get("title", domain),
            "explanation":  data.get("explanation", ""),
            "points":       data.get("key_points", []),
            "real_world":   data.get("example", ""),
            "questions":    [],
            "summary":      data.get("difficulty_note", ""),
            "sources":      data.get("sources", []),
            "ai_generated": True,
        }
    except Exception as exc:
        logger.warning(f"FastAPI /learn failed: {exc}")
        return {
            "topic": domain,
            "explanation": f"Failed to reach FastAPI backend (port 8000) for '{domain}'. Make sure uvicorn is running.",
            "points": ["Check FastAPI server status.", "Ensure Ollama is active on port 11434."],
            "real_world": "Troubleshooting API connections.",
            "questions": [],
            "summary": "Check API logs.",
            "sources": [],
            "ai_generated": False
        }

def _get_content(domain: str, level: str) -> dict:
    """
    Loads content dynamically via API and caches it in session state.
    """
    cache_key = f"_learning_cache_{domain}_{level}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    content = _fetch_learning_content(domain, level)
    st.session_state[cache_key] = content
    return content

def _stream_content(url):
    """Stream request generator logic to pass safely into write_stream."""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=16, decode_unicode=True):
            if chunk:
                yield chunk

def render():
    inject_global_css()
    st.markdown("""
<style>
.learn-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.2;
    margin-bottom: 0.3rem;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

    if not st.session_state.get("quiz_attempted", False):
        st.markdown("""
<div style="display:flex;justify-content:center;align-items:center;min-height:50vh;">
  <div style="background:rgba(255,255,255,0.04);backdrop-filter:blur(12px);
              border:1px solid rgba(255,255,255,0.08);border-radius:16px;
              padding:2.5rem 3rem;text-align:center;max-width:480px;
              box-shadow:0 8px 32px rgba(0,0,0,0.3);">
    <div style="font-size:2.5rem;margin-bottom:0.75rem;">⚠️</div>
    <div style="font-size:1.15rem;font-weight:700;color:#FFFFFF;margin-bottom:1rem;">
      Please attempt the quiz first before accessing learning content.
    </div>
  </div>
</div>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Go to Quiz", use_container_width=True):
                st.session_state.page = "Quiz"
                st.rerun()
        st.stop()

    domain = st.session_state.get("selected_domain", "Networking")
    score  = st.session_state.get("score", 0)
    level  = "Intermediate" # default simplified for UI proxy map
    
    st.markdown('<div class="als-page-title"><img src="https://img.icons8.com/fluency/512/open-book.png" width="24" style="vertical-align:-5px; margin-right:5px;"> Learning Room (Live Stream)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="als-page-subtitle">Targeted material for <strong>{domain}</strong></div>', unsafe_allow_html=True)

    # Main Learning Content Area
    st.markdown(f'<div class="learn-title">{domain}</div>', unsafe_allow_html=True)
    st.markdown('<hr class="als-divider">', unsafe_allow_html=True)

    with st.spinner(f"Generating optimized learning path for {domain}..."):
        content = _get_content(domain, level)

    if content.get("summary"):
        st.info(content["summary"])

    st.markdown("### Explanation")
    st.write(content["explanation"])

    if content.get("points"):
        st.markdown("### Key Points")
        for point in content["points"]:
            st.markdown(f"- {point}")

    if content.get("real_world"):
        st.markdown("### Real World Example")
        st.success(content["real_world"])

    if content.get("sources"):
        st.markdown('### <img src="https://img.icons8.com/fluency/512/globe.png" width="24" style="vertical-align:-5px; margin-right:5px;"> Reliable Sources', unsafe_allow_html=True)
        for source in content["sources"]:
            title = source.get("title", "External Link")
            url = source.get("url", "#")
            st.markdown(f"- [{title}]({url})")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Start Targeted Quiz", use_container_width=True):
            for k,v in [("question_num",1),("score",0),("current_question",None),
                        ("diff_scores",{"Easy":{"correct":0,"total":0},"Medium":{"correct":0,"total":0},"Hard":{"correct":0,"total":0}})]:
                st.session_state[k] = v
            st.session_state.page = "Quiz"
            st.rerun()
    with c2:
        if st.button("View Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()

    # ── Eduna! Floating AI Chatbot ──
    render_eduna_chatbot()
