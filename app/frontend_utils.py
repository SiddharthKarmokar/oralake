import streamlit as st
import html

def apply_custom_css():
    st.markdown("""
    <style>
    html { scroll-behavior: smooth; }

    /* Navbar */
    .nav-bar {
        position: sticky;
        top: 0;
        z-index: 999;
        background: #ffffff;
        padding: 10px 0;
        text-align: center;
        box-shadow: 0 1px 6px rgba(0,0,0,0.1);
    }
    .nav-bar a {
        margin: 0 15px;
        text-decoration: none;
        font-weight: 600;
        color: #10a37f;
    }
    .nav-bar a:hover {
        color: #0d856a;
    }

    /* Section styling */
    section {
        background: #f9fafb;
        border-radius: 16px;
        padding: 25px;
        margin: 40px auto;
        max-width: 900px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)



#######################
# ---------- Visual Theme / Animations ----------
def apply_animated_css():
    st.markdown("""
    <style>
    /* GENERIC: fade/pulse */
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes pulse { 0%,100%{ transform: scale(1); opacity:0.9 } 50%{ transform: scale(1.06); opacity:1 } }

    /* Success animation */
    .ol-success { text-align:center; animation:fadeIn .45s ease-in; color:#0f5132; }
    .ol-success .circle { display:inline-block; width:56px; height:56px; border-radius:50%;
                          background: linear-gradient(180deg,#bbf7d0,#4ade80); box-shadow:0 8px 20px rgba(16,185,129,.15);
                          animation:pulse 1.6s infinite; margin-bottom:8px; }
    .ol-success p { margin:0; font-weight:600; color:#065f46; }

    /* Error */
    .ol-error { text-align:center; animation:fadeIn .45s ease-in; color:#7f1d1d; }
    .ol-error .cross { display:inline-block; width:56px; height:56px; border-radius:50%;
                       background: linear-gradient(180deg,#fecaca,#f87171); box-shadow:0 8px 20px rgba(248,113,113,.12);
                       animation:pulse 1.6s infinite; margin-bottom:8px; }
    .ol-error p { margin:0; font-weight:600; color:#7f1d1d; }

    /* Info / Tag */
    .ol-info { text-align:center; animation:fadeIn .45s ease-in; color:#075985; }
    .ol-info .tag { display:inline-block; font-size:28px; padding:8px; border-radius:10px;
                    background: linear-gradient(180deg,#bfdbfe,#93c5fd); margin-bottom:8px; animation:pulse 1.4s infinite; }
    .ol-info p { margin:0; font-weight:600; color:#075985; }

    /* shimmer placeholder for loading */
    .ol-shimmer {
      height:72px; border-radius:12px; margin:8px 0;
      background: linear-gradient(90deg, #f3f4f6 0%, #e6eef9 50%, #f3f4f6 100%);
      background-size: 200% 100%;
      animation: shimmer 1.2s linear infinite;
    }
    @keyframes shimmer {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    /* Subtle card glow for results */
    .ol-card { border-radius:12px; padding:12px; background:linear-gradient(180deg,#ffffff,#fbfdff);
               box-shadow: 0 8px 30px rgba(16,24,40,0.06); margin-bottom:10px; animation:fadeIn .35s ease; }
    </style>
    """, unsafe_allow_html=True)


# ---------- Small helper functions (global API) ----------
def alert(message: str, level: str = "info"):
    """
    Minimal change API. Use alert("text", "success"|"error"|"info"|"warning").
    This renders an animated block. Keeps your UX consistent.
    """
    safe = html.escape(str(message))
    if level == "success":
        st.markdown(f"""<div class="ol-success"><div class="circle"></div><p>{safe}</p></div>""", unsafe_allow_html=True)
    elif level == "error":
        st.markdown(f"""<div class="ol-error"><div class="cross"></div><p>{safe}</p></div>""", unsafe_allow_html=True)
    elif level == "warning":
        st.markdown(f"""<div class="ol-info"><div class="tag">⚠️</div><p>{safe}</p></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="ol-info"><div class="tag">ℹ️</div><p>{safe}</p></div>""", unsafe_allow_html=True)


def show_shimmer(placeholder_area):
    """
    Minimal shimmer: call ph = st.empty(); ph.markdown(show_shimmer(...))
    But we provide helper that returns the placeholder and you can clear it later via ph.empty()
    Example:
        ph = show_shimmer()
        ... long process ...
        ph.empty()
    """
    ph = st.empty()
    ph.markdown('<div class="ol-shimmer"></div>', unsafe_allow_html=True)
    return ph
