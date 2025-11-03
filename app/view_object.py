# import streamlit as st
# import requests
# from frontend_utils import apply_custom_css, alert, show_shimmer


# def render_view_object():
#     """Render the View Object section in the Oracle Data Lake Portal."""
#     apply_custom_css()

#     with st.container():
#         st.markdown("<h2 id='view-section'>🧾 View Object</h2>", unsafe_allow_html=True)
#         st.write("Retrieve and view stored objects from the Oracle Data Lake by their Object ID.")

#         # --- Input Field ---
#         object_id = st.text_input("Enter Object ID:", placeholder="e.g., 101", key="view_object_input")

#         # --- Fetch Button ---
#         if st.button("Fetch Object", use_container_width=True, key="view_object_button"):
#             if not object_id:
#                 st.warning("⚠️ Please enter a valid Object ID.")
#                 return

#             with st.spinner("🔍 Fetching object details..."):
#                 try:
#                     response = requests.get(f"http://localhost:8000/oracle/{object_id}")

#                     if response.status_code == 200:
#                         data = response.json()

#                         # ✅ Display success
#                         st.success("✅ Object retrieved successfully!")

#                         # Display data in a formatted block
#                         if isinstance(data, dict):
#                             st.json(data)
#                         else:
#                             st.write(data)

#                         # --- Optional Meta Info ---
#                         version = data.get("version")
#                         timestamp = data.get("timestamp")

#                         meta_info = []
#                         if version:
#                             meta_info.append(f"📘 **Version:** {version}")
#                         if timestamp:
#                             meta_info.append(f"🕒 **Timestamp:** {timestamp}")

#                         if meta_info:
#                             st.markdown("<br>".join(meta_info), unsafe_allow_html=True)

#                     elif response.status_code == 404:
#                         st.warning("⚠️ Object not found in the Oracle Data Lake.")
#                     else:
#                         st.error(f"❌ Server error {response.status_code}: {response.text}")

#                 except Exception as e:
#                     st.error(f"⚠️ Error: {e}")

#     st.markdown("---")


import streamlit as st
import requests
from frontend_utils import apply_animated_css, alert, show_shimmer


def render_view_object():
    """Render the View Object section in the Oracle Data Lake Portal."""
    apply_animated_css()

    with st.container():
        st.markdown("<h2 id='view-section'>🧾 View Object</h2>", unsafe_allow_html=True)
        st.write("Retrieve and view stored objects from the Oracle Data Lake by their Object ID.")

        # --- Input Field ---
        object_id = st.text_input("Enter Object ID:", placeholder="e.g., 101", key="view_object_input")

        # --- Fetch Button ---
        if st.button("Fetch Object", use_container_width=True, key="view_object_button"):
            if not object_id:
                alert("Please enter a valid Object ID.", "warning")
                return

            shimmer = show_shimmer(st)
            try:
                response = requests.get(f"http://localhost:8000/oracle/{object_id}")
                shimmer.empty()

                if response.status_code == 200:
                    data = response.json()

                    alert("Object retrieved successfully!", "success")

                    # --- Display meta info in animated card ---
                    meta_info = []
                    if isinstance(data, dict):
                        version = data.get("version")
                        timestamp = data.get("timestamp")

                        if version:
                            meta_info.append(f"📘 <b>Version:</b> {version}")
                        if timestamp:
                            meta_info.append(f"🕒 <b>Timestamp:</b> {timestamp}")

                        st.markdown(
                            f"""
                            <div class="ol-card">
                                <h4>📦 Object ID: {object_id}</h4>
                                {"<br>".join(meta_info) if meta_info else ""}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # --- Pretty display for object data ---
                        st.json(data)
                    else:
                        st.markdown(
                            f"<div class='ol-card'><p>{data}</p></div>",
                            unsafe_allow_html=True
                        )

                elif response.status_code == 404:
                    alert("Object not found in the Oracle Data Lake.", "info")
                else:
                    alert(f"Server error {response.status_code}: {response.text}", "error")

            except Exception as e:
                shimmer.empty()
                alert(f"Error: {e}", "error")

    st.markdown("---")
