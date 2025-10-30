import streamlit as st
import requests
from frontend_utils import apply_custom_css
apply_custom_css()

st.set_page_config(page_title="Tag Object", layout="wide")
st.title("🏷️ Tag Object")

# --- Backend URL ---
FASTAPI_URL = "http://127.0.0.1:8000/tag-object"  # adjust if different

st.markdown("Use this form to tag an existing object in the Oracle Data Lake.")

# --- Input Fields ---
object_id = st.text_input("Object ID", placeholder="Enter object ID (e.g., 101)")
tag = st.text_input("Tag", placeholder="Enter tag (e.g., analytics, model, raw-data)")
description = st.text_area("Description (optional)", placeholder="Enter short description")
schema_hint = st.text_area("Schema Hint (optional)", placeholder="Example: JSON, CSV, Parquet")

# --- Submit Button ---
if st.button("Tag Object"):
    if not object_id or not tag:
        st.error("Object ID and Tag are required.")
    else:
        with st.spinner("Tagging object..."):
            try:
                payload = {
                    "object_id": int(object_id),
                    "tag": tag,
                    "description": description or None,
                    "schema_hint": schema_hint or None,
                }
                response = requests.post(FASTAPI_URL, json=payload)

                if response.status_code == 200 and response.json().get("success"):
                    st.success(f"✅ Object {object_id} tagged successfully with '{tag}'.")
                else:
                    st.error(f"❌ Failed to tag object. Server said: {response.text}")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
