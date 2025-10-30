# src/frontend_utils.py
import streamlit as st
from pathlib import Path

def apply_custom_css():
    """Applies the global custom Streamlit CSS once."""
    css_path = Path("assets/style.css")
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
