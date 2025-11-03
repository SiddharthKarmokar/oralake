# import streamlit as st
# import requests
# import base64
# from frontend_utils import apply_custom_css, alert, show_shimmer

# def render_get_object():
#     apply_custom_css()

#     with st.container():
#         st.markdown("<h2 id='get-section'>📥 Retrieve Object from Data Lake</h2>", unsafe_allow_html=True)
#         st.write("Fetch stored objects and metadata directly from the Oracle Data Lake using their Object ID.")

#         # --- Input ---
#         object_id = st.text_input("Enter Object ID to fetch", placeholder="e.g., 101")

#         # --- Button ---
#         if st.button("Fetch Object", use_container_width=True):
#             if not object_id.strip():
#                 st.warning("Please enter a valid Object ID.")
#             else:
#                 with st.spinner("Fetching object..."):
#                     try:
#                         response = requests.get(f"http://localhost:8000/datalake/get/{object_id}")
                        
#                         if response.status_code == 200:
#                             data = response.json()
#                             filename = data.get("filename", f"object_{object_id}")
#                             file_content = base64.b64decode(data["content"])

#                             # ✅ Display object details
#                             st.success(f"✅ Object fetched successfully! ({filename})")
#                             st.toast("Object fetched successfully!", icon="📦")

#                             # --- Version Info (if backend sends it) ---
#                             if "version" in data:
#                                 st.info(f"📘 Version: {data['version']}")
#                             if "timestamp" in data:
#                                 st.caption(f"🕒 Uploaded on: {data['timestamp']}")

#                             # --- Download Option ---
#                             st.download_button(
#                                 label="⬇️ Download File",
#                                 data=file_content,
#                                 file_name=filename,
#                                 mime=data.get("type", "application/octet-stream")
#                             )

#                         elif response.status_code == 404:
#                             st.error("❌ Object not found.")
#                         else:
#                             st.error(f"⚠️ Failed to fetch object. Error: {response.text}")

#                     except Exception as e:
#                         st.error(f"⚠️ Error: {e}")

#     st.markdown("---")



import streamlit as st
import requests
import base64
from frontend_utils import apply_animated_css, alert, show_shimmer

def render_get_object():
    apply_animated_css()

    with st.container():
        st.markdown("<h2 id='get-section'>📥 Retrieve Object from Data Lake</h2>", unsafe_allow_html=True)
        st.write("Fetch stored objects and metadata directly from the Oracle Data Lake using their Object ID.")

        # --- Input ---
        object_id = st.text_input("Enter Object ID to fetch", placeholder="e.g., 101")

        # --- Button ---
        if st.button("Fetch Object", use_container_width=True):
            if not object_id.strip():
                alert("Please enter a valid Object ID.", "warning")
            else:
                shimmer = show_shimmer(st)
                try:
                    response = requests.get(f"http://localhost:8000/datalake/get/{object_id}")
                    shimmer.empty()

                    if response.status_code == 200:
                        data = response.json()
                        filename = data.get("filename", f"object_{object_id}")
                        file_content = base64.b64decode(data["content"])

                        # ✅ Animated Success
                        alert(f"Object '{filename}' fetched successfully!", "success")

                        # --- Version Info (if backend sends it) ---
                        if "version" in data:
                            st.markdown(f"<div class='ol-card'>📘 Version: {data['version']}</div>", unsafe_allow_html=True)
                        if "timestamp" in data:
                            st.caption(f"🕒 Uploaded on: {data['timestamp']}")

                        # --- Download Option ---
                        st.download_button(
                            label="⬇️ Download File",
                            data=file_content,
                            file_name=filename,
                            mime=data.get("type", "application/octet-stream")
                        )

                    elif response.status_code == 404:
                        alert("Object not found.", "error")
                    else:
                        alert(f"Failed to fetch object. Error: {response.text}", "error")

                except Exception as e:
                    shimmer.empty()
                    alert(f"Error: {e}", "error")

    st.markdown("---")
