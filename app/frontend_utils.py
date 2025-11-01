import streamlit as st

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
