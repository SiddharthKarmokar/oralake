import streamlit as st
from frontend_utils import apply_custom_css
apply_custom_css()

st.set_page_config(page_title="Oracle Data Lake", page_icon="💧")
st.title("Oracle Data Lake Dashboard")

st.sidebar.success("Select a page above ⬆️")

st.markdown("""
Welcome to the Data Lake visualization and management interface.
Use the sidebar to:
- 📤 Upload files
- 🔍 Search or view objects
""")
