# import streamlit as st
# import requests
# from frontend_utils import apply_custom_css
# apply_custom_css()

# st.title("Oracle Data Viewer")

# # Input from user
# user_input = st.text_input("Enter some ID:")

# if st.button("Fetch Data"):
#     try:
#         # Call FastAPI endpoint
#         response = requests.get(f"http://localhost:8000/oracle/{user_input}")
#         data = response.json()
#         st.write(data)
#     except Exception as e:
#         st.error(f"Error: {e}")


# import streamlit as st
# import requests
# from frontend_utils import apply_custom_css

# def render_view_object_section():
#     apply_custom_css()

#     with st.container():
#         st.markdown("<h2 id='view-section'>🧾 View Object</h2>", unsafe_allow_html=True)
#         st.write("Retrieve and view stored objects from the Oracle Data Lake by their ID.")

#         user_input = st.text_input("Enter Object ID:", placeholder="e.g., 101")

#         if st.button("Fetch Data", use_container_width=True):
#             if not user_input:
#                 st.warning("Please enter a valid Object ID.")
#                 return

#             with st.spinner("🔍 Fetching object details..."):
#                 try:
#                     response = requests.get(f"http://localhost:8000/oracle/{user_input}")
#                     if response.status_code == 200:
#                         data = response.json()

#                         # --- Display Object Details ---
#                         st.success("✅ Object retrieved successfully!")
#                         st.json(data)

#                         # Optional: detect and display version info if present
#                         if "version" in data:
#                             st.info(f"📘 Version: {data['version']}")

#                     elif response.status_code == 404:
#                         st.warning("⚠️ Object not found.")
#                     else:
#                         st.error(f"Server error {response.status_code}: {response.text}")

#                 except Exception as e:
#                     st.error(f"⚠️ Error: {e}")

#     st.markdown("---")


import streamlit as st
import requests
from frontend_utils import apply_custom_css


def render_view_object():
    """Render the View Object section in the Oracle Data Lake Portal."""
    apply_custom_css()

    with st.container():
        st.markdown("<h2 id='view-section'>🧾 View Object</h2>", unsafe_allow_html=True)
        st.write("Retrieve and view stored objects from the Oracle Data Lake by their Object ID.")

        # --- Input Field ---
        object_id = st.text_input("Enter Object ID:", placeholder="e.g., 101", key="view_object_input")

        # --- Fetch Button ---
        if st.button("Fetch Object", use_container_width=True, key="view_object_button"):
            if not object_id:
                st.warning("⚠️ Please enter a valid Object ID.")
                return

            with st.spinner("🔍 Fetching object details..."):
                try:
                    response = requests.get(f"http://localhost:8000/oracle/{object_id}")

                    if response.status_code == 200:
                        data = response.json()

                        # ✅ Display success
                        st.success("✅ Object retrieved successfully!")

                        # Display data in a formatted block
                        if isinstance(data, dict):
                            st.json(data)
                        else:
                            st.write(data)

                        # --- Optional Meta Info ---
                        version = data.get("version")
                        timestamp = data.get("timestamp")

                        meta_info = []
                        if version:
                            meta_info.append(f"📘 **Version:** {version}")
                        if timestamp:
                            meta_info.append(f"🕒 **Timestamp:** {timestamp}")

                        if meta_info:
                            st.markdown("<br>".join(meta_info), unsafe_allow_html=True)

                    elif response.status_code == 404:
                        st.warning("⚠️ Object not found in the Oracle Data Lake.")
                    else:
                        st.error(f"❌ Server error {response.status_code}: {response.text}")

                except Exception as e:
                    st.error(f"⚠️ Error: {e}")

    st.markdown("---")
