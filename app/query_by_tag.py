# import streamlit as st
# import requests
# import pandas as pd
# from frontend_utils import apply_custom_css
# apply_custom_css()


# st.title("🔍 Search Data Lake by Tag")

# tag = st.text_input("Enter tag to search:")

# if st.button("Search"):
#     with st.spinner("Searching objects..."):
#         try:
#             response = requests.get(f"http://localhost:8000/datalake/query-by-tag/{tag}")
#             data = response.json()

#             if data["status"] == "success":
#                 st.success(f"✅ Found {data['count']} objects for tag '{tag}'")
#                 df = pd.DataFrame(data["objects"], columns=["Object_Blob"])
#                 st.dataframe(df)
#                 st.balloons()
#             elif data["status"] == "empty":
#                 st.warning(data["message"])
#             else:
#                 st.error("❌ Unexpected response. Try again later.")
#         except Exception as e:
#             st.error(f"Error: {e}")


import streamlit as st
import requests
import pandas as pd
from frontend_utils import apply_custom_css

def render_query_by_tag():
    apply_custom_css()

    with st.container():
        st.markdown("<h2 id='query-section'>🔍 Query Data Lake by Tag</h2>", unsafe_allow_html=True)
        st.write("Search and explore objects stored in the Oracle Data Lake using tags.")

        tag = st.text_input("Enter tag to search:")

        if st.button("Search", use_container_width=True):
            if not tag:
                st.warning("Please enter a tag to search.")
                return

            with st.spinner("🔎 Searching objects..."):
                try:
                    response = requests.get(f"http://localhost:8000/datalake/query-by-tag/{tag}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data["status"] == "success":
                            count = data.get("count", 0)
                            objects = data.get("objects", [])
                            st.success(f"✅ Found {count} object(s) for tag '{tag}'")

                            if objects:
                                df = pd.DataFrame(objects)
                                # Format DataFrame
                                if "object_id" in df.columns:
                                    df.rename(columns={"object_id": "Object ID"}, inplace=True)
                                if "version" in df.columns:
                                    df.rename(columns={"version": "Version"}, inplace=True)
                                st.dataframe(df, use_container_width=True)
                                st.balloons()
                            else:
                                st.warning("No objects found.")

                        elif data["status"] == "empty":
                            st.warning(data["message"])
                        else:
                            st.error("❌ Unexpected response. Try again later.")
                    else:
                        st.error(f"⚠️ Server returned status code {response.status_code}")

                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
