import streamlit as st
import requests
import time

st.title("📤 Upload to Oracle Data Lake")

uploaded_file = st.file_uploader("Choose a file to upload")
tags = st.text_input("Tags (comma separated)")
description = st.text_area("Description")

if st.button("Upload"):
    if uploaded_file is not None:
        with st.spinner("Uploading file to Data Lake..."):
            files = {"file": uploaded_file.getvalue()}
            data = {"tags": tags, "description": description}
            response = requests.post("http://localhost:8000/datalake/upload", files=files, data=data)
            time.sleep(1)

        if response.status_code == 200:
            st.success("✅ File uploaded successfully!")
            st.balloons()
        else:
            st.error("❌ Upload failed!")
            st.snow()
