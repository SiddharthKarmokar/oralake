import streamlit as st
import requests

st.title("Oracle Data Viewer")

# Input from user
user_input = st.text_input("Enter some ID:")

if st.button("Fetch Data"):
    try:
        # Call FastAPI endpoint
        response = requests.get(f"http://localhost:8000/oracle/{user_input}")
        data = response.json()
        st.write(data)
    except Exception as e:
        st.error(f"Error: {e}")
