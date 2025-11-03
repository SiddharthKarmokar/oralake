# import streamlit as st
# import requests
# import time
# from frontend_utils import apply_custom_css, alert, show_shimmer

# def render_add_object():
#     apply_custom_css()
    
#     with st.container():
#         st.markdown("<h2 id='add-section'>📤 Add / Upload Object</h2>", unsafe_allow_html=True)
#         st.write("Upload your object to the Oracle Data Lake with tags and schema hints. Version tracking is automatically handled.")

#         # File uploader
#         file = st.file_uploader("Choose a file to upload", type=["csv", "txt", "json", "xlsx", "pdf", "png", "jpg"])
#         tags = st.text_input("Tags (comma-separated)")
#         description = st.text_area("Description")
#         schema_hint = st.text_input("Schema Hint (optional)")

#         # Upload button
#         if st.button("Upload", use_container_width=True):
#             if not file:
#                 st.warning("Please select a file first.")
#             else:
#                 with st.spinner("📡 Uploading... Please wait."):
#                     try:
#                         files = {"file": (file.name, file.getvalue())}
#                         data = {
#                             "tags": tags,
#                             "description": description,
#                             "schema_hint": schema_hint
#                         }
#                         response = requests.post(
#                             "http://localhost:8000/datalake/upload",
#                             files=files,
#                             data=data
#                         )

#                         if response.status_code == 200:
#                             res = response.json()
#                             if res.get("status") == "success":
#                                 object_id = res.get("object_id")
#                                 version = res.get("version", 1)

#                                 st.session_state["last_uploaded_object"] = {
#                                     "object_id": object_id,
#                                     "version": version
#                                 }

#                                 st.success(f"✅ File uploaded successfully!")
#                                 st.info(f"🆔 **Object ID:** {object_id} | 📄 **Version:** {version}")
#                                 st.toast("Object added successfully!", icon="🎉")
#                                 time.sleep(1)
#                                 st.snow()
#                             else:
#                                 st.error("❌ Failed to add object. Please try again.")
#                         else:
#                             st.error(f"⚠️ Server Error: {response.status_code}")

#                     except Exception as e:
#                         st.error(f"⚠️ Error: {e}")

#     st.markdown("---")


import streamlit as st
import requests
import time
from frontend_utils import apply_animated_css, alert, show_shimmer

def render_add_object():
    # Apply global animated CSS (replaces old custom css)
    apply_animated_css()
    
    with st.container():
        st.markdown("<h2 id='add-section'>📤 Add / Upload Object</h2>", unsafe_allow_html=True)
        st.write("Upload your object to the Oracle Data Lake with tags and schema hints. Version tracking is automatically handled.")

        # File uploader
        file = st.file_uploader("Choose a file to upload", type=["csv", "txt", "json", "xlsx", "pdf", "png", "jpg"])
        tags = st.text_input("Tags (comma-separated)")
        description = st.text_area("Description")
        schema_hint = st.text_input("Schema Hint (optional)")

        # Upload button
        if st.button("Upload", use_container_width=True):
            if not file:
                alert("Please select a file first.", "warning")
            else:
                # Show shimmer animation while uploading
                ph = show_shimmer(st)
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
                finally:
                    # Remove shimmer in all cases
                    ph.empty()

                # --- Handle response ---
                if response.status_code == 200:
                    res = response.json()
                    if res.get("status") == "success":
                        object_id = res.get("object_id")
                        version = res.get("version", 1)

                        st.session_state["last_uploaded_object"] = {
                            "object_id": object_id,
                            "version": version
                        }

                        # Animated success alert
                        alert(f"File '{file.name}' uploaded successfully!", "success")
                        alert(f"🆔 Object ID: {object_id} | 📄 Version: {version}", "info")
                        st.toast("Object added successfully!", icon="🎉")
                        time.sleep(1)
                        st.snow()
                    else:
                        alert("Failed to add object. Please try again.", "error")
                else:
                    alert(f"Server Error: {response.status_code}", "error")

    st.markdown("---")
