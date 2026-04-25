import streamlit as st
from views.styles import inject_global_css

def render():
    inject_global_css()
    
    user_name = st.session_state.get("user_name", "Student")

    # Hero section
    st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
            min-height:72vh;text-align:center;padding:2rem 1rem;">

  <div style="background:rgba(132, 80, 179, 0.15);color:#D0B0F4;border:1px solid rgba(132, 80, 179, 0.2);
              backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
              border-radius:999px;padding:0.3rem 1.1rem;font-size:0.75rem;
              font-weight:700;text-transform:uppercase;letter-spacing:2px;
              margin-bottom:1.75rem;display:inline-block;">
    Welcome, {user_name}
  </div>

  <h1 style="font-family:'Inter',sans-serif;font-size:3.5rem;font-weight:800;
             color:#FFFFFF;line-height:1.15;margin-bottom:1rem;
             max-width:640px;text-shadow:0 2px 10px rgba(0,0,0,0.5);">
    SkillMap<span style="color:#8450B3;text-shadow:0 0 15px rgba(132,80,179,0.4);">.ai</span>
  </h1>

  <p style="font-size:1.05rem;color:rgba(255,255,255,0.65);max-width:480px;line-height:1.8;
            margin-bottom:2.5rem;">
    Personalised quizzes that adapt to your skill level.<br>
    Track progress, identify gaps, and reach mastery.
  </p>

</div>
""", unsafe_allow_html=True)

    # Centre the CTA button
    c1, c2, c3 = st.columns([1.6, 1, 1.6])
    with c2:
        if st.button("Start Learning →", use_container_width=True):
            st.session_state.page = "Domain"
            st.rerun()

    # Stats row
    st.markdown("""
<div style="display:flex;justify-content:center;gap:3rem;margin-top:3.5rem;flex-wrap:wrap;">
  <div style="text-align:center;">
    <div style="font-size:1.6rem;font-weight:800;color:#FFFFFF;text-shadow:0 2px 10px rgba(0,0,0,0.5);">4</div>
    <div style="font-size:0.75rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:1px;margin-top:0.15rem;">Domains</div>
  </div>
  <div style="text-align:center;">
    <div style="font-size:1.6rem;font-weight:800;color:#FFFFFF;text-shadow:0 2px 10px rgba(0,0,0,0.5);">3</div>
    <div style="font-size:0.75rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:1px;margin-top:0.15rem;">Difficulty Levels</div>
  </div>
  <div style="text-align:center;">
    <div style="font-size:1.6rem;font-weight:800;color:#FFFFFF;text-shadow:0 2px 10px rgba(0,0,0,0.5);">6</div>
    <div style="font-size:0.75rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:1px;margin-top:0.15rem;">Pages</div>
  </div>
</div>
""", unsafe_allow_html=True)
