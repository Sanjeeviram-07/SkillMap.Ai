"""
Eduna! — Floating AI Learning Assistant Chatbot
A modern, card-based chatbot UI for the Adaptive Learning System.
Uses Groq API (llama-3.1-8b-instant) for fast, concise responses.
"""

import logging
import asyncio
import streamlit as st
from services.groq_service import groq_service

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
EDUNA_SYSTEM_MSG = """You are Eduna, a friendly and concise AI learning assistant.

Rules:
- Keep responses short (2-4 sentences max unless the user asks for detail).
- Be encouraging and supportive.
- If asked about a topic, explain it simply and clearly.
- Use bullet points for lists.
- Never say "As an AI..." — just answer directly.
- If you don't know something, say so honestly.
"""

EDUNA_MODEL = "llama-3.1-8b-instant"


# ── Chat Logic ────────────────────────────────────────────────────────────────

def _init_eduna_state():
    """Initialize session state keys for Eduna chatbot."""
    if "eduna_open" not in st.session_state:
        st.session_state.eduna_open = False
    if "eduna_history" not in st.session_state:
        st.session_state.eduna_history = []


def _get_eduna_response(user_message: str) -> str:
    """
    Call Groq API synchronously from Streamlit using asyncio.
    Returns the assistant's response string.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            groq_service.generate_response(
                prompt=user_message,
                system_message=EDUNA_SYSTEM_MSG,
                model=EDUNA_MODEL,
                temperature=0.6,
            )
        )
        loop.close()
        return response
    except Exception as e:
        logger.error(f"Eduna Groq API error: {e}")
        return "Sorry, I'm having trouble connecting right now. Please try again in a moment."


# ── CSS ───────────────────────────────────────────────────────────────────────

EDUNA_CSS = """
<style>

/* ══════════════════════════════════════════
   EDUNA CARD — COMPLETE SELF-CONTAINED CARD
   ══════════════════════════════════════════ */

.eduna-card-wrap {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 22px;
    box-shadow: 0 8px 36px rgba(0,0,0,0.3);
    overflow: hidden;
    margin-top: 1.5rem;
    animation: eduna-slide-in 0.35s cubic-bezier(0.22, 1, 0.36, 1);
    display: flex;
    flex-direction: column;
}

@keyframes eduna-slide-in {
    from { opacity: 0; transform: translateY(24px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0)   scale(1); }
}

/* ── Header ── */
.eduna-hdr {
    background: linear-gradient(135deg, rgba(132, 80, 179, 0.3) 0%, rgba(132, 80, 179, 0.05) 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 1.1rem 1.4rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.eduna-hdr-left {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}
.eduna-hdr-avatar {
    width: 42px;
    height: 42px;
    background: rgba(255,255,255,0.22);
    border-radius: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.35rem;
    flex-shrink: 0;
}
.eduna-hdr-title {
    font-size: 1rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 0.3px;
    margin: 0;
}
.eduna-hdr-sub {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.82);
    margin: 0.1rem 0 0;
}

/* ── Chat Messages Area ── */
.eduna-messages {
    background: transparent;
    padding: 1.1rem 1.2rem;
    min-height: 220px;
    max-height: 420px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    scroll-behavior: smooth;
}

/* ── Empty State ── */
.eduna-empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2.5rem 1.5rem;
    color: rgba(255,255,255,0.65);
}
.eduna-empty .icon { font-size: 2.8rem; margin-bottom: 0.6rem; }
.eduna-empty .title { font-weight: 700; color: #FFFFFF; font-size: 1rem; margin-bottom: 0.25rem; }
.eduna-empty .sub   { font-size: 0.82rem; }

/* ── Message Bubbles ── */
.emsg {
    max-width: 82%;
    padding: 0.72rem 1rem;
    font-size: 0.88rem;
    line-height: 1.6;
    border-radius: 18px;
    word-break: break-word;
    transition: opacity 0.3s ease;
}
.emsg-user {
    background: #8450B3;
    color: #FFFFFF;
    align-self: flex-end;
    border-bottom-right-radius: 5px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.emsg-bot {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.08);
    align-self: flex-start;
    border-bottom-left-radius: 5px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
.emsg-bot .bot-label {
    font-size: 0.68rem;
    font-weight: 700;
    color: #D0B0F4;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 0.3rem;
    display: block;
}

/* ── Input Area (inside card) ── */
.eduna-input-bar {
    background: transparent;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding: 0.9rem 1.2rem;
}

/* Override Streamlit form styling to match card input */
div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
    background: transparent !important;
}

/* Style the text input inside the card */
.eduna-card-wrap div[data-testid="stTextInput"] input {
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    background: rgba(255, 255, 255, 0.04) !important;
    color: #FFFFFF !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.9rem !important;
    box-shadow: none !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.eduna-card-wrap div[data-testid="stTextInput"] input:focus {
    border-color: #8450B3 !important;
    box-shadow: inset 0 0 0 1px rgba(132, 80, 179, 0.5) !important;
    background: rgba(255, 255, 255, 0.06) !important;
}
.eduna-card-wrap div[data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.4) !important;
}

/* Style send button inside the card */
.eduna-card-wrap div[data-testid="stFormSubmitButton"] button {
    background: #8450B3 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.2rem !important;
    height: auto !important;
    box-shadow: 0 4px 16px rgba(132,80,179,0.3) !important;
    transition: background 0.2s ease, transform 0.15s ease !important;
    width: 100%;
}
.eduna-card-wrap div[data-testid="stFormSubmitButton"] button:hover {
    background: #643A8C !important;
    transform: translateY(-1px) !important;
}

/* ── Divider ── */
.eduna-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.08);
    margin: 0;
}

/* ── Spinner override ── */
.eduna-thinking {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.65);
    padding: 0.4rem 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    align-self: flex-start;
}

/* ── Remove global chat_input black bar ── */
div[data-testid="stChatInput"],
section[data-testid="stBottom"],
.stChatFloatingInputContainer {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}

</style>
"""


# ── Public Render Function ────────────────────────────────────────────────────

def render_eduna_chatbot():
    """
    Renders the Eduna chatbot as a complete, self-contained card.
    The chat input is embedded inside the card — no external black bar.
    """
    _init_eduna_state()
    st.markdown(EDUNA_CSS, unsafe_allow_html=True)

    # ── Closed State: Show compact toggle button ──────────────────────────────
    if not st.session_state.eduna_open:
        cols = st.columns([5, 1])
        with cols[1]:
            if st.button("💬 Eduna!", key="eduna_open_btn", use_container_width=True):
                st.session_state.eduna_open = True
                st.rerun()
        return

    # ── Open State: Render Full Card ──────────────────────────────────────────
    
    # Open card wrapper
    st.markdown('<div class="eduna-card-wrap">', unsafe_allow_html=True)

    # ── 1. Header ────────────────────────────────────────────────────────────
    st.markdown("""
<div class="eduna-hdr">
    <div class="eduna-hdr-left">
        <div class="eduna-hdr-avatar">🎓</div>
        <div>
            <p class="eduna-hdr-title">Eduna Assistant</p>
            <p class="eduna-hdr-sub">Powered by Groq · Llama 3.1</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── 2. Close Button (Streamlit — must be native for interactivity) ────────
    _, close_col = st.columns([8, 1])
    with close_col:
        if st.button("✕", key="eduna_close_btn", use_container_width=True, help="Close chat"):
            st.session_state.eduna_open = False
            st.rerun()

    # ── 3. Chat Messages Area ─────────────────────────────────────────────────
    if not st.session_state.eduna_history:
        st.markdown("""
<div class="eduna-messages">
    <div class="eduna-empty">
        <div class="icon">✨</div>
        <div class="title">Hi! I'm Eduna.</div>
        <div class="sub">Ask me anything about your learning topic below.</div>
    </div>
</div>
""", unsafe_allow_html=True)
    else:
        bubbles_html = ""
        for msg in st.session_state.eduna_history:
            if msg["role"] == "user":
                bubbles_html += f'<div class="emsg emsg-user">{msg["content"]}</div>'
            else:
                bubbles_html += f"""
<div class="emsg emsg-bot">
    <span class="bot-label">🎓 Eduna</span>
    {msg["content"]}
</div>"""

        st.markdown(f"""
<div class="eduna-messages" id="eduna-msgs">
    {bubbles_html}
</div>
<script>
    (function() {{
        var el = document.getElementById('eduna-msgs');
        if (el) el.scrollTop = el.scrollHeight;
    }})();
</script>
""", unsafe_allow_html=True)

    # ── 4. Input Area (inside the card) ──────────────────────────────────────
    st.markdown('<div class="eduna-input-bar">', unsafe_allow_html=True)

    with st.form(key="eduna_form", clear_on_submit=True):
        input_col, btn_col = st.columns([5, 1])
        with input_col:
            user_input = st.text_input(
                label="",
                placeholder="Ask Eduna anything...",
                key="eduna_text_input",
                label_visibility="collapsed",
            )
        with btn_col:
            submitted = st.form_submit_button("Send ↑", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Close card wrapper
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 5. Process Submitted Message ──────────────────────────────────────────
    if submitted and user_input and user_input.strip():
        st.session_state.eduna_history.append({"role": "user", "content": user_input.strip()})
        with st.spinner("Eduna is thinking..."):
            response = _get_eduna_response(user_input.strip())
        st.session_state.eduna_history.append({"role": "assistant", "content": response})
        st.rerun()
