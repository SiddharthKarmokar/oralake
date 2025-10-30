import streamlit as st
import requests
import base64
from frontend_utils import apply_custom_css
apply_custom_css()

st.title("📥 Retrieve Object from Data Lake")

object_id = st.text_input("Enter Object ID to fetch")

if st.button("Fetch Object"):
    if not object_id.strip():
        st.warning("Please enter a valid Object ID.")
    else:
        with st.spinner("Fetching object..."):
            try:
                response = requests.get(f"http://localhost:8000/datalake/get/{object_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    filename = data.get("filename", f"object_{object_id}")
                    file_content = base64.b64decode(data["content"])

                    # Show file info
                    st.success(f"✅ Object fetched successfully! ({filename})")
                    st.toast("Object fetched successfully!", icon="📦")

                    # Provide download button
                    st.download_button(
                        label="⬇️ Download File",
                        data=file_content,
                        file_name=filename,
                        mime=data.get("type", "application/octet-stream")
                    )

                elif response.status_code == 404:
                    st.error("❌ Object not found.")
                else:
                    st.error(f"⚠️ Failed to fetch object. Error: {response.text}")

            except Exception as e:
                st.error(f"Error: {e}")
