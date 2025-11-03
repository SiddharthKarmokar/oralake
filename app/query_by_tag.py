# import streamlit as st
# import requests
# import pandas as pd
# from frontend_utils import apply_custom_css, alert, show_shimmer

# def render_query_by_tag():
#     apply_custom_css()

#     with st.container():
#         st.markdown("<h2 id='query-section'>🔍 Query Data Lake by Tag</h2>", unsafe_allow_html=True)
#         st.write("Search and explore objects stored in the Oracle Data Lake using tags.")

#         tag = st.text_input("Enter tag to search:")

#         if st.button("Search", use_container_width=True):
#             if not tag:
#                 st.warning("Please enter a tag to search.")
#                 return

#             with st.spinner("🔎 Searching objects..."):
#                 try:
#                     response = requests.get(f"http://localhost:8000/datalake/query-by-tag/{tag}")
                    
#                     if response.status_code == 200:
#                         data = response.json()
#                         if data["status"] == "success":
#                             count = data.get("count", 0)
#                             objects = data.get("objects", [])
#                             st.success(f"✅ Found {count} object(s) for tag '{tag}'")

#                             if objects:
#                                 df = pd.DataFrame(objects)
#                                 # Format DataFrame
#                                 if "object_id" in df.columns:
#                                     df.rename(columns={"object_id": "Object ID"}, inplace=True)
#                                 if "version" in df.columns:
#                                     df.rename(columns={"version": "Version"}, inplace=True)
#                                 st.dataframe(df, use_container_width=True)
#                                 st.balloons()
#                             else:
#                                 st.warning("No objects found.")

#                         elif data["status"] == "empty":
#                             st.warning(data["message"])
#                         else:
#                             st.error("❌ Unexpected response. Try again later.")
#                     else:
#                         st.error(f"⚠️ Server returned status code {response.status_code}")

#                 except Exception as e:
#                     st.error(f"Error: {e}")

#     st.markdown("---")


import streamlit as st
import requests
from frontend_utils import apply_animated_css, alert, show_shimmer

def render_query_by_tag():
    apply_animated_css()

    with st.container():
        st.markdown("<h2 id='query-section'>🔍 Query Objects by Tag</h2>", unsafe_allow_html=True)
        st.write("Search Oracle Data Lake objects based on tags, schema, or descriptions.")

        # --- Inputs ---
        tag_query = st.text_input("Enter Tag or Keyword", placeholder="e.g., analytics, model, report")
        schema_hint = st.text_input("Schema Hint (optional)", placeholder="e.g., CSV, JSON, Image")

        # --- Button ---
        if st.button("Search", use_container_width=True):
            if not tag_query.strip():
                alert("Please enter a tag or keyword.", "warning")
            else:
                shimmer = show_shimmer(st)
                try:
                    response = requests.get(
                        f"http://127.0.0.1:8000/query-by-tag",
                        params={"tag": tag_query, "schema_hint": schema_hint}
                    )
                    shimmer.empty()

                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])

                        if results:
                            alert(f"Found {len(results)} matching objects!", "success")

                            # --- Display Results in Beautiful Cards ---
                            for obj in results:
                                st.markdown(
                                    f"""
                                    <div class="ol-card">
                                        <h4>📘 Object ID: {obj.get('object_id', 'N/A')}</h4>
                                        <p><b>Tag:</b> {obj.get('tag', '-')}</p>
                                        <p><b>Description:</b> {obj.get('description', '-')}</p>
                                        <p><b>Schema:</b> {obj.get('schema_hint', '-')}</p>
                                        <p><b>Version:</b> {obj.get('version', '-')}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        else:
                            alert("No objects found for the given tag or schema.", "info")
                    else:
                        alert(f"Server error: {response.status_code}", "error")

                except Exception as e:
                    shimmer.empty()
                    alert(f"Error: {e}", "error")

    st.markdown("---")
