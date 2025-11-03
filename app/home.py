import streamlit as st
from add_object import render_add_object
from tag_object import render_tag_object
from query_by_tag import render_query_by_tag
from get_object import render_get_object
from view_object import render_view_object
from frontend_utils import apply_custom_css, apply_animated_css

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="Oracle Data Lake Portal",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# Custom Theme + Scroll
# ---------------------------
#apply_custom_css()

apply_animated_css()


st.set_page_config(page_title="Oracle Data Lake", page_icon="💧")
st.title("Oracle Data Lake Dashboard")

st.sidebar.success("Select a page above ⬆️")

st.markdown("""
Welcome to the unified **Oracle Data Lake Dashboard**.  
Here you can:
- 📤 Add and Upload Objects  
- 🏷️ Tag and Manage Objects  
- 🔍 Query Objects by Tag  
- 📦 Retrieve Object Metadata  
- 👁️ View Object Content and Version History  
All within one **smooth, single-page interface** styled with the *Anthropic Light* theme.
""")

# ---------------------------
# Sticky Navigation Bar
# ---------------------------
st.markdown("""
<div class="nav-bar">
    <a href="#add-section">➕ Add Object</a>
    <a href="#tag-section">🏷️ Tag Object</a>
    <a href="#query-section">🔍 Query by Tag</a>
    <a href="#get-section">📦 Get Object</a>
    <a href="#view-section">👁️ View Object</a>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# Section 1: Add Object
# ---------------------------
st.markdown('<div id="add-section"></div>', unsafe_allow_html=True)
render_add_object()

# ---------------------------
# Section 2: Tag Object
# ---------------------------
st.markdown('<div id="tag-section"></div>', unsafe_allow_html=True)
render_tag_object()

# ---------------------------
# Section 3: Query by Tag
# ---------------------------
st.markdown('<div id="query-section"></div>', unsafe_allow_html=True)
render_query_by_tag()

# ---------------------------
# Section 4: Get Object
# ---------------------------
st.markdown('<div id="get-section"></div>', unsafe_allow_html=True)
render_get_object()

# ---------------------------
# Section 5: View Object
# ---------------------------
st.markdown('<div id="view-section"></div>', unsafe_allow_html=True)
render_view_object()

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.success("📂 Use the top navigation bar or scroll to explore sections.")
