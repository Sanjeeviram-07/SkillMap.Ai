import streamlit as st
import streamlit.components.v1 as components
import os
import re

from services.db_service import (
    init_db, signup_user, login_user,
    get_or_create_google_user,
)

# ── Firebase Google Auth Component ──

_component_func = components.declare_component(
    "google_auth",
    path=os.path.join(os.path.dirname(__file__), "google_auth_component"),
)


def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def firebase_google_login(comp_key="google_auth_btn"):
    """Render the Firebase Google login component and handle results."""
    result = _component_func(key=comp_key, default=None)

    if result and isinstance(result, dict) and "uid" in result:
        email = result.get("email")
        name = result.get("name", "Google User")

        user = get_or_create_google_user(email, name)

        if user:
            st.session_state["user"] = user
            st.session_state["user_name"] = user["name"]
            st.rerun()


# ── CSS ──

def inject_auth_css():
    st.markdown("""
<style>
/* ---- Page chrome ---- */
header[data-testid="stHeader"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
footer { display: none !important; }

html, body { margin: 0; padding: 0; }

/* Gradient dark-to-slate full-page background */
.stApp {
    background: linear-gradient(140deg, #1a1a2e 0%, #2d2b55 55%, #3b3769 100%) !important;
}

/* Strip block-container default padding */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

/* ---- Slide-in animation ---- */
@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Transform the native container into the actual Card */
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) {
    animation: slideUp 0.4s ease-out;
    background: rgba(255, 255, 255, 0.75) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-radius: 16px !important;
    padding: 2.5rem 2.25rem 2rem !important;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    width: 100% !important;
    max-width: 420px !important;
    margin: 0 auto !important;
    align-self: center !important;
}

/* Force dark text globally inside the card against Streamlit's dark theme */
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) * {
    color: #2C2C2C !important;
}

/* ---- Card header ---- */
.auth-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #2C2C2C !important;
    margin-bottom: 0.25rem;
    text-align: center;
    font-family: 'Inter', sans-serif;
}
.auth-subtitle {
    font-size: 0.9rem;
    color: #6B7280 !important;
    text-align: center;
    margin-bottom: 1.8rem;
    font-family: 'Inter', sans-serif;
}

/* ---- Inputs ---- */
/* Overall wrapper (input + eye icon) shares true white background */
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) .stTextInput div[data-baseweb="input"],
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) .stSelectbox > div > div {
    background-color: #FFFFFF !important;
    border: 1.5px solid #CBCBCB !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
    overflow: hidden !important; 
}

/* Remove Streamlit's inner dark background for base-input */
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) div[data-baseweb="base-input"] {
    background-color: transparent !important;
}

/* Actual input text field formatting */
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) .stTextInput input {
    background-color: transparent !important;
    color: #2C2C2C !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1rem !important;
    border: none !important;
    -webkit-text-fill-color: #2C2C2C !important; /* Forces dark text */
}

/* Prevent browser autofill from darkening the background */
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) .stTextInput input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0 1000px #FFFFFF inset !important;
    -webkit-text-fill-color: #2C2C2C !important;
}

/* Focus highlighting */
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) .stTextInput div[data-baseweb="input"]:focus-within,
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) .stSelectbox > div > div:focus-within {
    border-color: #6D8196 !important;
    box-shadow: 0 0 0 3px rgba(109, 129, 150, 0.15) !important;
}

div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) .stTextInput input::placeholder { color: #9CA3AF !important; }

/* Labels */
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) [data-testid="stWidgetLabel"] p {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #4A4A4A !important;
    letter-spacing: 0.2px !important;
    text-transform: none !important;
    margin-bottom: 6px !important;
}

/* ---- Primary button (submit) ---- */
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) div[data-testid="stButton"] button {
    background: #6D8196 !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    height: 48px !important;
    border: none !important;
    border-radius: 10px !important;
    width: 100% !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s ease !important;
    margin-top: 1rem !important;
}
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) div[data-testid="stButton"] button p {
    color: #FFFFFF !important; /* Force button text white */
}
div[data-testid="stVerticalBlock"]:has(> div:first-child .auth-title) div[data-testid="stButton"] button:hover {
    background: #5a6b7d !important;
    box-shadow: 0 6px 15px rgba(109, 129, 150, 0.3) !important;
    color: #FFFFFF !important;
    border: none !important;
    transform: translateY(-1px);
}

/* Secondary toggle button placed outside form */
div.stButton > button {
    background: transparent !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 10px !important;
    height: 44px !important;
    width: 100% !important;
    max-width: 420px !important;
    margin: 0 auto !important;
    display: block !important;
    transition: all 0.2s !important;
}
div.stButton > button p {
    color: #FFFFFF !important;
}
div.stButton > button:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: #FFFFFF !important;
}

/* ---- Toggle label text ---- */
.auth-switch-text {
    text-align: center;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.8);
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}

/* ---- Errors / success ---- */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.9rem !important;
    margin-top: 1rem !important;
}

/* ---- Divider ---- */
.auth-divider {
    display: flex;
    align-items: center;
    text-align: center;
    margin: 0.8rem 0;
    color: #9CA3AF;
    font-size: 0.85rem;
    font-family: 'Inter', sans-serif;
}
.auth-divider::before,
.auth-divider::after {
    content: '';
    flex: 1;
    border-bottom: 1px solid #E5E7EB;
}
.auth-divider:not(:empty)::before { margin-right: .5em; }
.auth-divider:not(:empty)::after { margin-left: .5em; }

/* Spaces */
div[data-testid="stVerticalBlock"] > div { gap: 0.6rem; }
</style>
""", unsafe_allow_html=True)


# ── RENDER ──

def render():
    init_db()

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "signin"

    inject_auth_css()

    if st.session_state.auth_mode == "signin":
        _render_signin()
    else:
        _render_signup()


def _render_signin():
    with st.container():
        st.markdown("""
            <div class="auth-title">Welcome Back</div>
            <div class="auth-subtitle">Sign in to continue</div>
        """, unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="name@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.button("Sign In", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                success, result = login_user(email, password)
                if success:
                    st.session_state["user"] = result
                    st.session_state["user_name"] = result["name"]
                    st.rerun()
                else:
                    st.error(result)

        st.markdown("<div class='auth-divider'>or</div>", unsafe_allow_html=True)
        firebase_google_login("signin")

    st.markdown('<div class="auth-switch-text">Don\'t have an account?</div>', unsafe_allow_html=True)
    if st.button("Create Account", key="go_signup", use_container_width=True):
        st.session_state.auth_mode = "signup"
        st.rerun()


def _render_signup():
    with st.container():
        st.markdown("""
            <div class="auth-title">Create Account</div>
            <div class="auth-subtitle">Sign up to begin your learning journey</div>
        """, unsafe_allow_html=True)

        name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="name@example.com")

        pc1, pc2 = st.columns(2)
        with pc1:
            password = st.text_input("Password", type="password", placeholder="••••••••")
        with pc2:
            confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")

        domain = st.selectbox("Primary Domain",
                              ["Networking", "AI & ML", "Cloud Computing", "Business Analyst"])

        submitted = st.button("Create Account", use_container_width=True)

        if submitted:
            if not all([name, email, password, confirm]):
                st.error("Please fill in all fields.")
            elif not validate_email(email):
                st.error("Enter a valid email address.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                ok, msg = signup_user(name, email, password, domain)
                if ok:
                    st.success(msg)
                    st.session_state.auth_mode = "signin"
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("<div class='auth-divider'>or</div>", unsafe_allow_html=True)
        firebase_google_login("signup")

    st.markdown('<div class="auth-switch-text">Already have an account?</div>', unsafe_allow_html=True)
    if st.button("Sign In", key="go_signin", use_container_width=True):
        st.session_state.auth_mode = "signin"
        st.rerun()
