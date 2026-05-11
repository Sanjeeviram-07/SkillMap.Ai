import streamlit as st
from views.styles import inject_global_css
from views import home, domain, quiz, result, learning, dashboard, pdf_chat, auth
from services.db_service import init_db

# ── Page Config ──
st.set_page_config(
    page_title="SkillMap.ai",
    page_icon="https://img.icons8.com/fluency/512/graduation-cap.png",
    layout="wide"
)

# ── Session Init ──
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

# ── Route Map ──
routes = {
    "Home":      home.render,
    "Domain":    domain.render,
    "Quiz":      quiz.render,
    "Result":    result.render,
    "Learning":  learning.render,
    "Dashboard": dashboard.render,
    "PDF Chat":  pdf_chat.render,
}

# ── Global CSS ──
inject_global_css()

# ── Navigation Pane CSS ──
st.markdown("""
<style>

/* Main padding */
section.main > div {
    padding-top: 1rem;
}

/* Block container - relax for column layout */
.block-container {
    max-width: 100% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Main content area */
.main-content-wrapper {
    max-width: 1060px;
    margin: 0 auto;
    padding: 0.5rem 2rem 3rem 2rem;
}

/* Logo */
.logo {
    text-align: center;
    padding: 1rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 1.5rem;
}

/* Active nav */
.active-nav {
    background: linear-gradient(90deg, rgba(132,80,179,0.3), transparent);
    border-left: 4px solid #8450B3;
    padding: 0.6rem;
    border-radius: 8px;
    margin-bottom: 5px;
    font-weight: 600;
    color: white;
}

/* Hide default Streamlit sidebar completely */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"] {
    display: none !important;
    visibility: hidden !important;
}

</style>
""", unsafe_allow_html=True)

# ── Auth Check ──
if "user" not in st.session_state:
    auth.render()
    st.stop()

# ── Toggle Button ──
toggle_col, _ = st.columns([0.05, 0.95])

with toggle_col:
    if st.session_state.sidebar_open:
        if st.button("<<", key="close_sidebar", help="Close Sidebar"):
            st.session_state.sidebar_open = False
            st.rerun()
    else:
        if st.button(">>", key="open_sidebar", help="Open Sidebar"):
            st.session_state.sidebar_open = True
            st.rerun()

# ── Layout ──
if st.session_state.sidebar_open:
    sidebar_col, gap_col, main_col = st.columns([0.20, 0.03, 0.77])
else:
    sidebar_col, gap_col, main_col = st.columns([0.05, 0.03, 0.92])

# ── Sidebar ──
with sidebar_col:
    if st.session_state.sidebar_open:

        # Logo
        st.markdown("""
<div class="logo">
  <div style="font-size:2rem;"><img src="https://img.icons8.com/fluency/512/graduation-cap.png" width="48"></div>
  <div style="font-weight:800;font-size:1.2rem;color:white;">SkillMap.ai</div>
  <div style="font-size:0.7rem;color:gray;">Beta · v1.0</div>
</div>
""", unsafe_allow_html=True)

        NAV = [
            ("Home",      "https://img.icons8.com/fluency/512/home.png"),
            ("Domain",    "https://img.icons8.com/fluency/512/puzzle.png"),
            ("Quiz",      "https://img.icons8.com/fluency/512/edit-property.png"),
            ("Result",    "https://img.icons8.com/fluency/512/bar-chart.png"),
            ("Learning",  "https://img.icons8.com/fluency/512/open-book.png"),
            ("Dashboard", "https://img.icons8.com/fluency/512/positive-dynamic.png"),
            ("PDF Chat",  "https://img.icons8.com/fluency/512/document.png"),
        ]

        active = st.session_state.page

        for page_name, icon in NAV:
            if active == page_name:
                st.markdown(
                    f'<div class="active-nav"><img src="{icon}" width="24" style="vertical-align:-5px; margin-right:8px;"> {page_name}</div>',
                    unsafe_allow_html=True
                )
            else:
                col1, col2 = st.columns([0.15, 0.85], gap="small")
                with col1:
                    st.markdown(f'<div style="margin-top:10px;"><img src="{icon}" width="24"></div>', unsafe_allow_html=True)
                with col2:
                    if st.button(page_name, key=f"nav_{page_name}", use_container_width=True):
                        st.session_state.page = page_name
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([0.15, 0.85], gap="small")
        with col1:
            st.markdown(f'<div style="margin-top:10px;"><img src="https://img.icons8.com/fluency/512/exit.png" width="24"></div>', unsafe_allow_html=True)
        with col2:
            if st.button("Logout", use_container_width=True):
                del st.session_state["user"]
                st.rerun()

# ── Main Content ──
with main_col:
    st.markdown('<div class="main-content-wrapper">', unsafe_allow_html=True)
    if st.session_state.page in routes:
        routes[st.session_state.page]()
    else:
        st.error(f"Page '{st.session_state.page}' not found.")
    st.markdown('</div>', unsafe_allow_html=True)

# Trigger reload
init_db()
