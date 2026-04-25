"""
Adaptive Learning System — Design System
Palette: Cream / Light Grey / Dark Grey / Muted Blue
"""
import streamlit as st

FONT_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Serif+Display&display=swap"

# ── New Deep Dark Premium Theme ──
# Note: Instead of a flat BG colour, the user requested a gradient. We handle this directly in the CSS string below.
# These constants are kept mostly for fallback or non-gradient elements.
BG          = "#1F1C2E" 
BG_CARD     = "rgba(255, 255, 255, 0.04)"
GREY_LIGHT  = "rgba(255, 255, 255, 0.15)"
GREY_MID    = "#9BA8B5"
TEXT        = "#F1F1F3"
TEXT_MUTED  = "rgba(255, 255, 255, 0.65)"
ACCENT      = "#8450B3"
ACCENT_DARK = "#643A8C"
ACCENT_SOFT = "rgba(132, 80, 179, 0.15)"
BORDER      = "rgba(255, 255, 255, 0.08)"
SUCCESS     = "#4EBE7B"
DANGER      = "#D95C5C"
WARNING     = "#D1A551"


def inject_global_css():
    st.markdown(f"""
        <style>
        @import url('{FONT_URL}');

        /* ── Reset ── */
        #MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] {{
            visibility: hidden; display: none;
        }}

        html, body, .stApp {{
            background: linear-gradient(135deg, #43405F 0%, #2C293F 50%, #1F1C2E 100%) !important;
            background-attachment: fixed !important;
            color: {TEXT};
            font-family: 'Inter', sans-serif;
            /* Disable text selection */
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
        }}

        /* ── Block container ── */
        .block-container {{
            padding: 1.5rem 1rem 3rem 1rem !important;
            max-width: 100% !important;
        }}

        /* ════════════════════════════════════════
           SIDEBAR NAV BUTTONS
        ════════════════════════════════════════ */
        [data-testid="stSidebar"] .stButton > button {{
            background: transparent !important;
            color: {TEXT_MUTED} !important;
            border: 1px solid transparent !important;
            border-radius: 8px !important;
            text-align: left !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            padding: 0.55rem 1rem !important;
            width: 100% !important;
            box-shadow: none !important;
            transition: all 0.25s ease !important;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: {ACCENT_SOFT} !important;
            color: #FFFFFF !important;
            border-left: 3px solid {ACCENT} !important;
            box-shadow: 0 0 15px rgba(132, 80, 179, 0.2) !important;
        }}

        /* ════════════════════════════════════════
           GLOBAL ACTION BUTTONS
        ════════════════════════════════════════ */
        .stButton > button {{
            background: {ACCENT} !important;
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            padding: 0.7rem 1.6rem !important;
            border-radius: 10px !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(132,80,179,0.3) !important;
            transition: all 0.2s ease !important;
            letter-spacing: 0.01em !important;
        }}
        .stButton > button:hover {{
            background: {ACCENT_DARK} !important;
            box-shadow: 0 6px 20px rgba(132,80,179,0.4) !important;
            transform: translateY(-1px) !important;
        }}
        .stButton > button:active {{
            transform: translateY(0px) !important;
        }}

        /* ════════════════════════════════════════
           RADIO BUTTONS
        ════════════════════════════════════════ */
        .stRadio > div {{
            gap: 0.5rem;
        }}
        .stRadio > div > label {{
            background: {BG_CARD} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 12px !important;
            padding: 0.8rem 1.1rem !important;
            transition: all 0.18s ease !important;
            color: {TEXT} !important;
            cursor: pointer;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }}
        .stRadio > div > label:hover {{
            border-color: rgba(132, 80, 179, 0.4) !important;
            background: {ACCENT_SOFT} !important;
            box-shadow: 0 0 10px rgba(132, 80, 179, 0.1) !important;
        }}
        .stRadio label p {{
            color: {TEXT} !important;
            font-size: 0.97rem;
        }}
        div[role="radiogroup"] label {{
            color: {TEXT} !important;
        }}

        /* ════════════════════════════════════════
           PROGRESS BAR
        ════════════════════════════════════════ */
        .stProgress > div > div > div {{
            background-color: {ACCENT} !important;
            border-radius: 999px;
            box-shadow: 0 0 10px rgba(132, 80, 179, 0.5) !important;
        }}
        .stProgress > div > div {{
            background-color: {GREY_LIGHT} !important;
            border-radius: 999px;
        }}

        /* ════════════════════════════════════════
           METRIC CARDS
        ════════════════════════════════════════ */
        div[data-testid="metric-container"] {{
            background: {BG_CARD} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 12px !important;
            padding: 1.4rem !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }}
        div[data-testid="metric-container"] label {{
            color: {TEXT_MUTED} !important;
            font-size: 0.75rem !important;
            text-transform: uppercase;
            letter-spacing: 1.2px;
        }}
        div[data-testid="metric-container"] [data-testid="metric-value"] {{
            color: #FFFFFF !important;
            font-size: 1.9rem !important;
            font-weight: 700 !important;
        }}

        /* ════════════════════════════════════════
           SELECTBOX & TEXT INPUT GLOBAL
        ════════════════════════════════════════ */
        .stSelectbox > div > div, .stTextInput > div > div > input {{
            background: {BG_CARD} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 10px !important;
            color: {TEXT} !important;
            backdrop-filter: blur(12px);
        }}
        .stTextInput > div > div > input:focus {{
            border-color: {ACCENT} !important;
            box-shadow: 0 0 0 3px rgba(132, 80, 179, 0.2) !important;
        }}

        /* ════════════════════════════════════════
           ALERTS
        ════════════════════════════════════════ */
        .stSuccess {{ border-radius: 12px !important; background: rgba(78, 190, 123, 0.1) !important; border: 1px solid rgba(78, 190, 123, 0.3) !important; color: #FFFFFF !important; }}
        .stError   {{ border-radius: 12px !important; background: rgba(217, 92, 92, 0.1) !important; border: 1px solid rgba(217, 92, 92, 0.3) !important; color: #FFFFFF !important; }}
        .stInfo    {{ border-radius: 12px !important; background: {ACCENT_SOFT} !important; border: 1px solid rgba(132, 80, 179, 0.3) !important; color: #FFFFFF !important; }}
        .stWarning {{ border-radius: 12px !important; background: rgba(209, 165, 81, 0.1) !important; border: 1px solid rgba(209, 165, 81, 0.3) !important; color: #FFFFFF !important; }}

        /* ════════════════════════════════════════
           SHARED COMPONENT CLASSES
        ════════════════════════════════════════ */

        /* Card (Glassmorphism) */
        .als-card {{
            background: {BG_CARD};
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 2rem 2.5rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            margin-bottom: 1.5rem;
        }}

        /* Page title */
        .als-page-title {{
            font-family: 'Inter', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 0.25rem;
            line-height: 1.2;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }}
        .als-page-subtitle {{
            font-size: 0.97rem;
            color: {TEXT_MUTED};
            margin-bottom: 2rem;
            line-height: 1.6;
        }}

        /* Section label */
        .als-section-title {{
            font-size: 0.72rem;
            font-weight: 700;
            color: {TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 2px;
            margin: 1.75rem 0 0.6rem 0;
        }}

        /* Badges */
        .als-badge {{
            display: inline-block;
            padding: 0.3rem 0.95rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        .badge-beginner     {{ background:rgba(217, 92, 92, 0.15); color:{DANGER}; border:1px solid rgba(217,92,92,0.3); }}
        .badge-intermediate {{ background:rgba(209, 165, 81, 0.15); color:{WARNING}; border:1px solid rgba(209,165,81,0.3); }}
        .badge-expert       {{ background:rgba(78, 190, 123, 0.15); color:{SUCCESS}; border:1px solid rgba(78,190,123,0.3); }}
        .badge-info         {{ background:{ACCENT_SOFT}; color:#D0B0F4; border:1px solid rgba(132, 80, 179, 0.3); }}

        /* Divider */
        .als-divider {{
            border: none;
            border-top: 1px solid {BORDER};
            margin: 1.25rem 0;
        }}

        /* Pill tag */
        .als-pill {{
            display: inline-block;
            background: {ACCENT_SOFT};
            color: #D0B0F4;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.2rem 0.75rem;
            border-radius: 999px;
            letter-spacing: 0.5px;
            border: 1px solid rgba(132, 80, 179, 0.2);
        }}
        </style>
    """, unsafe_allow_html=True)


def inject_anti_cheating_scripts():
    """
    Injects JavaScript to disable:
    - Right-click context menu
    - Copy (Ctrl+C)
    - View Source (Ctrl+U)
    - DevTools (F12, Ctrl+Shift+I)
    """
    st.markdown("""
        <script>
        // Disable Right-Click
        document.addEventListener('contextmenu', event => event.preventDefault());

        // Disable Copy
        document.addEventListener('copy', event => {
            event.preventDefault();
            console.log('Copying is disabled on this page.');
        });

        // Disable Key Shortcuts
        document.addEventListener('keydown', event => {
            // Disable Ctrl+C, Ctrl+U, Ctrl+S
            if (event.ctrlKey && (event.key === 'c' || event.key === 'u' || event.key === 's')) {
                event.preventDefault();
            }
            // Disable Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C (DevTools)
            if (event.ctrlKey && event.shiftKey && (event.key === 'I' || event.key === 'J' || event.key === 'C' || event.key === 'i' || event.key === 'j' || event.key === 'c')) {
                event.preventDefault();
            }
            // Disable F12 (DevTools)
            if (event.key === 'F12') {
                event.preventDefault();
            }
        });
        </script>
    """, unsafe_allow_html=True)
