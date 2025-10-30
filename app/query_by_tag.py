import streamlit as st
import requests
import pandas as pd
from frontend_utils import apply_custom_css
apply_custom_css()

st.set_page_config(page_title="Search by Tag", page_icon="🔍")

st.title("🔍 Search Data Lake by Tag")

tag = st.text_input("Enter tag to search:")

if st.button("Search"):
    with st.spinner("Searching objects..."):
        try:
            response = requests.get(f"http://localhost:8000/datalake/query-by-tag/{tag}")
            data = response.json()

            if data["status"] == "success":
                st.success(f"✅ Found {data['count']} objects for tag '{tag}'")
                df = pd.DataFrame(data["objects"], columns=["Object_Blob"])
                st.dataframe(df)
                st.balloons()
            elif data["status"] == "empty":
                st.warning(data["message"])
            else:
                st.error("❌ Unexpected response. Try again later.")
        except Exception as e:
            st.error(f"Error: {e}")
