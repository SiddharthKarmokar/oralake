import streamlit as st
import requests
import time
from frontend_utils import apply_custom_css
apply_custom_css()

st.title("📤 Upload Object to Data Lake")

# File uploader
file = st.file_uploader("Choose a file to upload")
tags = st.text_input("Tags (comma-separated)")
description = st.text_area("Description")
schema_hint = st.text_input("Schema Hint (optional)")

if st.button("Upload"):
    if not file:
        st.warning("Please select a file first.")
    else:
        with st.spinner("Uploading... Please wait."):
            try:
                files = {"file": (file.name, file.getvalue())}
                data = {
                    "tags": tags,
                    "description": description,
                    "schema_hint": schema_hint
                }
                response = requests.post(
                    "http://localhost:8000/datalake/upload",
                    files=files,
                    data=data
                )
                res = response.json()

                if res.get("status") == "success":
                    st.success(f"✅ File uploaded successfully! Object ID: {res['object_id']}")
                    st.toast("Object added successfully!", icon="🎉")
                    time.sleep(1)
                    st.snow()
                else:
                    st.error("❌ Failed to add object. Please try again.")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
