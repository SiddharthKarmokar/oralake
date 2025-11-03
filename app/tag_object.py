# import streamlit as st
# import requests
# from frontend_utils import apply_custom_css, alert, show_shimmer

# def render_tag_object():
#     apply_custom_css()

#     with st.container():
#         st.markdown("<h2 id='tag-section'>🏷️ Tag Existing Object</h2>", unsafe_allow_html=True)
#         st.write("Assign or update tags for existing Oracle Data Lake objects.")

#         # --- Backend URL ---
#         FASTAPI_URL = "http://127.0.0.1:8000/tag-object"  # adjust if needed

#         # --- Input Fields ---
#         object_id = st.text_input("Object ID", placeholder="Enter object ID (e.g., 101)")
#         tag = st.text_input("Tag", placeholder="Enter tag (e.g., analytics, model, raw-data)")
#         description = st.text_area("Description (optional)", placeholder="Enter short description")
#         schema_hint = st.text_area("Schema Hint (optional)", placeholder="Example: JSON, CSV, Parquet")

#         # --- Submit Button ---
#         if st.button("Tag Object", use_container_width=True):
#             if not object_id or not tag:
#                 st.error("❌ Object ID and Tag are required.")
#                 return

#             with st.spinner("🏷️ Tagging object..."):
#                 try:
#                     payload = {
#                         "object_id": int(object_id),
#                         "tag": tag.strip(),
#                         "description": description or None,
#                         "schema_hint": schema_hint or None,
#                     }
#                     response = requests.post(FASTAPI_URL, json=payload)

#                     if response.status_code == 200:
#                         res = response.json()
#                         if res.get("success"):
#                             st.success(f"✅ Object {object_id} tagged successfully with '{tag}'.")
#                             if res.get("version"):
#                                 st.info(f"📘 Current Version: {res['version']}")
#                         else:
#                             st.warning("⚠️ Tag operation completed, but server did not confirm success.")
#                     else:
#                         st.error(f"Server error: {response.status_code} — {response.text}")

#                 except Exception as e:
#                     st.error(f"⚠️ Error: {e}")

#     st.markdown("---")


import streamlit as st
import requests
from frontend_utils import apply_animated_css, alert, show_shimmer

def render_tag_object():
    apply_animated_css()

    with st.container():
        st.markdown("<h2 id='tag-section'>🏷️ Tag Existing Object</h2>", unsafe_allow_html=True)
        st.write("Assign or update tags for existing Oracle Data Lake objects.")

        FASTAPI_URL = "http://127.0.0.1:8000/tag-object"

        object_id = st.text_input("Object ID", placeholder="Enter object ID (e.g., 101)")
        tag = st.text_input("Tag", placeholder="Enter tag (e.g., analytics, model, raw-data)")
        description = st.text_area("Description (optional)", placeholder="Enter short description")
        schema_hint = st.text_area("Schema Hint (optional)", placeholder="Example: JSON, CSV, Parquet")

        if st.button("Tag Object", use_container_width=True):
            if not object_id or not tag:
                alert("❌ Object ID and Tag are required.", "error")
                return

            # --- Start shimmer animation while processing ---
            with st.spinner("🏷️ Tagging object..."):
                show_shimmer("Processing your request...")

                try:
                    payload = {
                        "object_id": int(object_id),
                        "tag": tag.strip(),
                        "description": description or None,
                        "schema_hint": schema_hint or None,
                    }
                    response = requests.post(FASTAPI_URL, json=payload)

                    if response.status_code == 200:
                        res = response.json()
                        if res.get("success"):
                            alert(f"✅ Object {object_id} tagged successfully with '{tag}'.", "success")
                            if res.get("version"):
                                st.markdown(f"<div class='fade-in'><b>📘 Current Version:</b> {res['version']}</div>", unsafe_allow_html=True)
                        else:
                            alert("⚠️ Tag operation completed, but server did not confirm success.", "warning")
                    else:
                        alert(f"Server error: {response.status_code} — {response.text}", "error")

                except Exception as e:
                    alert(f"⚠️ Error: {e}", "error")

    st.markdown("---")
