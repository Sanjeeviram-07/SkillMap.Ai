import streamlit as st
import asyncio
import logging
from services.pdf_service import extract_text_from_pdf, chunk_text_optimized
from services.rag_service import get_rag_service
from services.ai_service import generate_rag_answer, generate_text_response
from views.styles import inject_global_css

logger = logging.getLogger(__name__)

# ── CSS ───────────────────────────────────────────────────────────────────────
PDF_CHAT_CSS = """
<style>

/* ══════════════════════════════════════════
   PDF CHAT — SINGLE CARD LAYOUT
   ══════════════════════════════════════════ */

/* ── Main Card ── */
.pdf-main-card {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 22px;
    box-shadow: 0 8px 36px rgba(0,0,0,0.3);
    overflow: hidden;
    margin-top: 0.5rem;
    animation: pdf-slide-in 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes pdf-slide-in {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Card Header ── */
.pdf-hdr {
    background: linear-gradient(135deg, rgba(132, 80, 179, 0.3) 0%, rgba(132, 80, 179, 0.05) 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 1.25rem 1.6rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.pdf-hdr-icon {
    width: 46px;
    height: 46px;
    background: rgba(255,255,255,0.2);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.55rem;
    flex-shrink: 0;
}
.pdf-hdr-title {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 0.3px;
}
.pdf-hdr-sub {
    margin: 0.15rem 0 0;
    font-size: 0.73rem;
    color: rgba(255,255,255,0.82);
}

/* ── Upload Zone ── */
.pdf-upload-zone {
    background: transparent;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 1.1rem 1.5rem;
}
.pdf-upload-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 0.5rem;
}
.pdf-status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(78, 190, 123, 0.15);
    color: #4EBE7B;
    border: 1px solid rgba(78, 190, 123, 0.3);
    border-radius: 20px;
    padding: 0.3rem 0.85rem;
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 0.4rem;
}
.pdf-status-badge-wait {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(209, 165, 81, 0.15);
    color: #D1A551;
    border: 1px solid rgba(209, 165, 81, 0.3);
    border-radius: 20px;
    padding: 0.3rem 0.85rem;
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 0.4rem;
}

/* ── Chat Messages Area ── */
.pdf-messages-wrap {
    background: transparent;
    padding: 1rem 1.3rem;
    min-height: 260px;
    max-height: 420px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    scroll-behavior: smooth;
}

/* ── Empty States ── */
.pdf-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 3rem 1.5rem;
    color: rgba(255,255,255,0.65);
    min-height: 200px;
}
.pdf-empty .e-icon { font-size: 2.8rem; margin-bottom: 0.7rem; }
.pdf-empty .e-title { font-weight: 700; color: #FFFFFF; font-size: 1rem; margin-bottom: 0.3rem; }
.pdf-empty .e-sub { font-size: 0.83rem; max-width: 320px; }

/* ── Chat Bubbles ── */
.pmsg {
    max-width: 82%;
    padding: 0.75rem 1.05rem;
    font-size: 0.88rem;
    line-height: 1.65;
    border-radius: 18px;
    word-break: break-word;
}
.pmsg-user {
    background: #8450B3;
    color: #FFFFFF;
    align-self: flex-end;
    border-bottom-right-radius: 5px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.pmsg-bot {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.08);
    align-self: flex-start;
    border-bottom-left-radius: 5px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
.pmsg-bot .bot-tag {
    font-size: 0.68rem;
    font-weight: 700;
    color: #D0B0F4;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 0.35rem;
    display: block;
}

/* ── Input Bar ── */
.pdf-input-bar {
    background: transparent;
    border-top: 1px solid rgba(255,255,255,0.08);
    padding: 0.9rem 1.3rem;
}
.pdf-input-disabled-note {
    text-align: center;
    font-size: 0.8rem;
    color: rgba(255,255,255,0.4);
    padding: 0.75rem;
}

/* Override Streamlit form chrome */
.pdf-main-card div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
    background: transparent !important;
}

/* Style text input inside card */
.pdf-main-card div[data-testid="stTextInput"] input {
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    background: rgba(255, 255, 255, 0.04) !important;
    color: #FFFFFF !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.9rem !important;
    box-shadow: none !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.pdf-main-card div[data-testid="stTextInput"] input:focus {
    border-color: #8450B3 !important;
    box-shadow: inset 0 0 0 1px rgba(132, 80, 179, 0.5) !important;
    background: rgba(255, 255, 255, 0.06) !important;
}
.pdf-main-card div[data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.4) !important;
}
.pdf-main-card div[data-testid="stTextInput"] input:disabled {
    background: rgba(255, 255, 255, 0.02) !important;
    color: rgba(255,255,255,0.2) !important;
    cursor: not-allowed !important;
    border-color: rgba(255,255,255,0.04) !important;
}

/* Send button */
.pdf-main-card div[data-testid="stFormSubmitButton"] button {
    background: #8450B3 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.2rem !important;
    box-shadow: 0 4px 16px rgba(132,80,179,0.3) !important;
    transition: background 0.2s ease, transform 0.15s ease !important;
    width: 100%;
}
.pdf-main-card div[data-testid="stFormSubmitButton"] button:hover {
    background: #643A8C !important;
    transform: translateY(-1px) !important;
}
.pdf-main-card div[data-testid="stFormSubmitButton"] button:disabled {
    background: rgba(255,255,255,0.1) !important;
    box-shadow: none !important;
    transform: none !important;
    cursor: not-allowed !important;
    color: rgba(255,255,255,0.3) !important;
}

/* Process button */
.pdf-main-card div[data-testid="stButton"] button[kind="primary"] {
    background: #8450B3 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

/* ── Kill the external black chat bar ── */
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _init_state():
    if "pdf_chat_history" not in st.session_state:
        st.session_state.pdf_chat_history = []
    if "pdf_processed" not in st.session_state:
        st.session_state.pdf_processed = False
    if "pdf_doc_id" not in st.session_state:
        st.session_state.pdf_doc_id = None


def _process_pdf(uploaded_file):
    with st.spinner("Extracting and vectorizing PDF…"):
        pdf_bytes = uploaded_file.getvalue()
        text = extract_text_from_pdf(pdf_bytes)

        if not text:
            st.error("Failed to extract text. The file might be empty or corrupted.")
            return False

        chunks = chunk_text_optimized(text)

        try:
            rag = get_rag_service()
            rag.add_document(doc_id=uploaded_file.name, chunks=chunks)
            st.session_state.pdf_doc_id = uploaded_file.name
            st.session_state.pdf_processed = True
            return True
        except Exception as err:
            st.error(f"Error storing document: {err}")
            return False


def _answer_query(query: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        rag = get_rag_service()
        docs = rag.query(query, n_results=3, filter={"doc_id": st.session_state.pdf_doc_id})

        if docs:
            answer = loop.run_until_complete(generate_rag_answer(query, docs))
            if "Not found in document" in answer:
                fallback = (
                    f"The user asked a question about a document, but the document didn't "
                    f"contain the answer. Please answer based on your general knowledge if "
                    f"possible, but clarify that it is not from their document.\n\nQuestion: {query}"
                )
                answer = loop.run_until_complete(generate_text_response(fallback, task="learning"))
        else:
            fallback = (
                f"Please answer the following question based on your general knowledge. "
                f"Clarify that no relevant document context was found.\n\nQuestion: {query}"
            )
            answer = loop.run_until_complete(generate_text_response(fallback, task="learning"))

        return answer
    finally:
        loop.close()


# ── Main Render ───────────────────────────────────────────────────────────────

def render():
    inject_global_css()
    st.markdown(PDF_CHAT_CSS, unsafe_allow_html=True)
    _init_state()

    # Open main card
    st.markdown('<div class="pdf-main-card">', unsafe_allow_html=True)

    # ── 1. Header ────────────────────────────────────────────────────────────
    st.markdown("""
<div class="pdf-hdr">
    <div class="pdf-hdr-icon">📄</div>
    <div>
        <p class="pdf-hdr-title">PDF Chat Assistant</p>
        <p class="pdf-hdr-sub">Upload a document and ask intelligent questions</p>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── 2. Upload Zone ────────────────────────────────────────────────────────
    st.markdown('<div class="pdf-upload-zone">', unsafe_allow_html=True)
    st.markdown('<div class="pdf-upload-label">📤 Document Upload</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Select PDF", type=["pdf"], label_visibility="collapsed", key="pdf_uploader"
    )

    # Auto-process: trigger when a new (or first) file is uploaded
    if uploaded_file is not None:
        new_file = uploaded_file.name != st.session_state.get("pdf_doc_id")
        if new_file or not st.session_state.pdf_processed:
            with st.spinner("Processing document…"):
                _process_pdf(uploaded_file)
            st.rerun()

    # Status badge
    if st.session_state.pdf_processed and st.session_state.pdf_doc_id:
        st.markdown(
            f'<div class="pdf-status-badge">✅ Active — <strong>{st.session_state.pdf_doc_id}</strong></div>',
            unsafe_allow_html=True,
        )
    elif uploaded_file is not None:
        st.markdown(
            '<div class="pdf-status-badge-wait">⏳ Processing…</div>',
            unsafe_allow_html=True,
        )
    else:
        pass  # No badge needed when nothing is uploaded

    st.markdown("</div>", unsafe_allow_html=True)  # /upload-zone

    # ── 3. Chat Messages ──────────────────────────────────────────────────────
    if not st.session_state.pdf_processed:
        st.markdown("""
<div class="pdf-messages-wrap">
    <div class="pdf-empty">
        <div class="e-icon">📂</div>
        <div class="e-title">No Document Loaded</div>
        <div class="e-sub">Upload a PDF above to begin chatting.</div>
    </div>
</div>
""", unsafe_allow_html=True)

    elif not st.session_state.pdf_chat_history:
        st.markdown("""
<div class="pdf-messages-wrap">
    <div class="pdf-empty">
        <div class="e-icon">✨</div>
        <div class="e-title">Document Ready!</div>
        <div class="e-sub">Ask anything about your document using the input below.</div>
    </div>
</div>
""", unsafe_allow_html=True)

    else:
        bubbles = ""
        for msg in st.session_state.pdf_chat_history:
            if msg["role"] == "user":
                bubbles += f'<div class="pmsg pmsg-user">{msg["content"]}</div>'
            else:
                bubbles += f"""
<div class="pmsg pmsg-bot">
    <span class="bot-tag">📄 Assistant</span>
    {msg["content"]}
</div>"""

        st.markdown(f"""
<div class="pdf-messages-wrap" id="pdf-msgs">
    {bubbles}
</div>
<script>
    (function() {{
        var el = document.getElementById('pdf-msgs');
        if (el) el.scrollTop = el.scrollHeight;
    }})();
</script>
""", unsafe_allow_html=True)

    # ── 4. Input Bar (inside card) ────────────────────────────────────────────
    st.markdown('<div class="pdf-input-bar">', unsafe_allow_html=True)

    if st.session_state.pdf_processed:
        with st.form(key="pdf_chat_form", clear_on_submit=True):
            in_col, send_col = st.columns([5, 1])
            with in_col:
                query = st.text_input(
                    label="",
                    placeholder="Ask a question about your document...",
                    key="pdf_query_input",
                    label_visibility="collapsed",
                )
            with send_col:
                submitted = st.form_submit_button("Send ↑", use_container_width=True)
    else:
        # Show disabled-looking input when no doc is loaded
        st.markdown("""
<div style="display:flex;gap:0.75rem;align-items:center;">
    <input
        disabled
        placeholder="Upload and process a document first…"
        style="flex:1;padding:0.65rem 1rem;border-radius:14px;border:1px solid rgba(255,255,255,0.04);
               background:rgba(255,255,255,0.02);color:rgba(255,255,255,0.2);font-size:0.9rem;cursor:not-allowed;
               font-family:inherit;"
    />
    <button disabled style="padding:0.6rem 1.1rem;border-radius:12px;border:none;
        background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.3);font-weight:600;cursor:not-allowed;">
        Send ↑
    </button>
</div>
""", unsafe_allow_html=True)
        submitted = False
        query = None

    st.markdown("</div>", unsafe_allow_html=True)  # /input-bar

    # Close main card
    st.markdown("</div>", unsafe_allow_html=True)  # /pdf-main-card

    # ── 5. Process Query ─────────────────────────────────────────────────────
    if submitted and query and query.strip() and st.session_state.pdf_processed:
        st.session_state.pdf_chat_history.append({"role": "user", "content": query.strip()})
        with st.spinner("Searching document…"):
            try:
                answer = _answer_query(query.strip())
                st.session_state.pdf_chat_history.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Failed to generate answer: {e}")
        st.rerun()
