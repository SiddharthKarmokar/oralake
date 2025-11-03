# """
# OraLake Streamlit App - Media Storage Interface
# Interactive UI for managing images and videos with version control
# """

# import streamlit as st
# from pathlib import Path
# import io
# from PIL import Image
# from datetime import datetime
# import json
# from typing import Optional, List
# import sys

# # Import OraLake modules
# try:
#     from src.services.media_storage import MediaStorage, create_thumbnail, convert_image_format
#     from src.services.oralake import get_object, query_by_tag
#     from src.database import pool
#     import oracledb
#     ORALAKE_AVAILABLE = True
# except ImportError as e:
#     ORALAKE_AVAILABLE = False
#     st.error(f"⚠️ OraLake modules not available: {e}")


# # Page configuration
# st.set_page_config(
#     page_title="OraLake Media Manager",
#     page_icon="🗄️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 2.5rem;
#         font-weight: bold;
#         color: #1f77b4;
#         margin-bottom: 1rem;
#     }
#     .status-connected {
#         color: #28a745;
#         font-weight: bold;
#     }
#     .status-disconnected {
#         color: #dc3545;
#         font-weight: bold;
#     }
#     .metric-card {
#         background-color: #f0f2f6;
#         padding: 1rem;
#         border-radius: 0.5rem;
#         margin: 0.5rem 0;
#     }
#     .version-badge {
#         background-color: #007bff;
#         color: white;
#         padding: 0.2rem 0.5rem;
#         border-radius: 0.3rem;
#         font-size: 0.8rem;
#     }
# </style>
# """, unsafe_allow_html=True)


# def check_db_connection() -> bool:
#     """Check if database connection is available"""
#     if not ORALAKE_AVAILABLE:
#         return False
    
#     try:
#         with pool.acquire() as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT 1 FROM DUAL")
#             result = cursor.fetchone()
#             return result is not None
#     except Exception as e:
#         st.session_state.db_error = str(e)
#         return False


# def get_connection_status():
#     """Display database connection status in header"""
#     col1, col2, col3 = st.columns([3, 1, 1])
    
#     with col1:
#         st.markdown('<div class="main-header">🗄️ OraLake Media Manager</div>', 
#                    unsafe_allow_html=True)
    
#     with col2:
#         if st.button("🔄 Refresh Connection", use_container_width=True):
#             st.session_state.db_connected = check_db_connection()
#             st.rerun()
    
#     with col3:
#         is_connected = check_db_connection()
#         if is_connected:
#             st.markdown(
#                 '<div class="status-connected">🟢 Connected</div>', 
#                 unsafe_allow_html=True
#             )
#             st.session_state.db_connected = True
#         else:
#             st.markdown(
#                 '<div class="status-disconnected">🔴 Disconnected</div>', 
#                 unsafe_allow_html=True
#             )
#             st.session_state.db_connected = False
#             if hasattr(st.session_state, 'db_error'):
#                 st.error(f"Connection Error: {st.session_state.db_error}")


# def upload_image_tab():
#     """Tab for uploading images"""
#     st.header("📸 Upload Image")
    
#     if not st.session_state.get('db_connected', False):
#         st.warning("⚠️ Database not connected. Please check connection.")
#         return
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         uploaded_file = st.file_uploader(
#             "Choose an image file",
#             type=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff'],
#             help="Upload an image to store in OraLake"
#         )
        
#         if uploaded_file:
#             # Preview image
#             image = Image.open(uploaded_file)
#             st.image(image, caption="Preview", use_container_width=True)
            
#             # Image info
#             st.info(f"""
#             **Filename:** {uploaded_file.name}  
#             **Size:** {uploaded_file.size / 1024:.2f} KB  
#             **Dimensions:** {image.size[0]} x {image.size[1]} px  
#             **Format:** {image.format}
#             """)
    
#     with col2:
#         st.subheader("Image Settings")
        
#         object_name = st.text_input(
#             "Object Name",
#             value=Path(uploaded_file.name).stem if uploaded_file else "",
#             help="Unique name for this image"
#         )
        
#         tags = st.text_input(
#             "Tags",
#             value="image",
#             help="Comma-separated tags"
#         )
        
#         description = st.text_area(
#             "Description",
#             help="Optional description"
#         )
        
#         st.divider()
        
#         compress = st.checkbox("Compress Image", value=True)
        
#         if compress:
#             quality = st.slider(
#                 "Quality",
#                 min_value=50,
#                 max_value=100,
#                 value=85,
#                 help="JPEG quality (lower = smaller file)"
#             )
#         else:
#             quality = 95
        
#         max_dimension = st.number_input(
#             "Max Dimension (px)",
#             min_value=100,
#             max_value=5000,
#             value=2000,
#             step=100,
#             help="Maximum width or height"
#         )
        
#         st.divider()
        
#         if st.button("💾 Save Image", type="primary", use_container_width=True):
#             if not uploaded_file:
#                 st.error("Please upload an image first!")
#                 return
            
#             if not object_name:
#                 st.error("Please provide an object name!")
#                 return
            
#             try:
#                 with st.spinner("Saving image..."):
#                     # Save uploaded file temporarily
#                     temp_path = f"temp_{uploaded_file.name}"
#                     with open(temp_path, "wb") as f:
#                         f.write(uploaded_file.getbuffer())
                    
#                     # Save to OraLake
#                     obj_id = MediaStorage.save_image(
#                         file_path=temp_path,
#                         name=object_name,
#                         tags=tags,
#                         description=description,
#                         compress=compress,
#                         quality=quality,
#                         max_dimension=max_dimension
#                     )
                    
#                     # Clean up temp file
#                     Path(temp_path).unlink()
                    
#                     st.success(f"✅ Image saved successfully! ID: {obj_id}")
#                     st.balloons()
                    
#             except Exception as e:
#                 st.error(f"❌ Error saving image: {e}")

# def upload_video_tab():
#     """Tab for uploading videos"""
#     st.header("🎥 Upload Video")
    
#     if not st.session_state.get('db_connected', False):
#         st.warning("⚠️ Database not connected. Please check connection.")
#         return
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         uploaded_file = st.file_uploader(
#             "Choose a video file",
#             type=['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'],
#             help="Upload a video to store in OraLake",
#             key="video_uploader"  # Added unique key
#         )
        
#         if uploaded_file:
#             st.video(uploaded_file)
            
#             st.info(f"""
#             **Filename:** {uploaded_file.name}  
#             **Size:** {uploaded_file.size / (1024*1024):.2f} MB
#             """)
    
#     with col2:
#         st.subheader("Video Settings")
        
#         object_name = st.text_input(
#             "Object Name",
#             value=Path(uploaded_file.name).stem if uploaded_file else "",
#             help="Unique name for this video",
#             key="video_object_name"  # Added unique key
#         )
        
#         tags = st.text_input(
#             "Tags",
#             value="video",
#             help="Comma-separated tags",
#             key="video_tags"  # Added unique key
#         )
        
#         description = st.text_area(
#             "Description",
#             help="Optional description",
#             key="video_description"  # Added unique key - THIS WAS MISSING
#         )
        
#         st.divider()
        
#         if st.button("💾 Save Video", type="primary", use_container_width=True, key="save_video_btn"):
#             if not uploaded_file:
#                 st.error("Please upload a video first!")
#                 return
            
#             if not object_name:
#                 st.error("Please provide an object name!")
#                 return
            
#             try:
#                 with st.spinner("Saving video..."):
#                     # Save uploaded file temporarily
#                     temp_path = f"temp_{uploaded_file.name}"
#                     with open(temp_path, "wb") as f:
#                         f.write(uploaded_file.getbuffer())
                    
#                     # Save to OraLake
#                     obj_id = MediaStorage.save_video(
#                         file_path=temp_path,
#                         name=object_name,
#                         tags=tags,
#                         description=description
#                     )
                    
#                     # Clean up temp file
#                     Path(temp_path).unlink()
                    
#                     st.success(f"✅ Video saved successfully! ID: {obj_id}")
#                     st.balloons()
                    
#             except Exception as e:
#                 st.error(f"❌ Error saving video: {e}")

# def view_media_tab():
#     """Tab for viewing stored media"""
#     st.header("👁️ View Media")
    
#     if not st.session_state.get('db_connected', False):
#         st.warning("⚠️ Database not connected. Please check connection.")
#         return
    
#     col1, col2 = st.columns([1, 3])
    
#     with col1:
#         st.subheader("Retrieve by ID")
        
#         object_id = st.number_input(
#             "Object ID",
#             min_value=1,
#             step=1,
#             help="Enter the object ID to retrieve"
#         )
        
#         if st.button("🔍 Retrieve", use_container_width=True):
#             try:
#                 with st.spinner("Retrieving..."):
#                     content = get_object(object_id)
                    
#                     if content is None:
#                         st.error(f"Object with ID {object_id} not found!")
#                     else:
#                         st.session_state.current_object = content
#                         st.session_state.current_object_id = object_id
#                         st.success(f"✅ Retrieved object {object_id}")
                        
#             except Exception as e:
#                 st.error(f"❌ Error retrieving object: {e}")
        
#         st.divider()
        
#         st.subheader("Query by Tag")
        
#         tag_query = st.text_input(
#             "Tag",
#             value="image",
#             help="Search for objects with this tag"
#         )
        
#         if st.button("🔎 Search", use_container_width=True):
#             try:
#                 with st.spinner("Searching..."):
#                     objects = query_by_tag(tag_query)
                    
#                     if objects:
#                         st.session_state.search_results = objects
#                         st.success(f"✅ Found {len(objects)} objects")
#                     else:
#                         st.warning(f"No objects found with tag '{tag_query}'")
                        
#             except Exception as e:
#                 st.error(f"❌ Error searching: {e}")
    
#     with col2:
#         # Display current object
#         if hasattr(st.session_state, 'current_object'):
#             content = st.session_state.current_object
#             obj_id = st.session_state.current_object_id
            
#             st.subheader(f"Object ID: {obj_id}")
            
#             # Try to display as image
#             try:
#                 image = Image.open(io.BytesIO(content))
#                 st.image(image, caption=f"Object {obj_id}", use_container_width=True)
                
#                 # Image info
#                 col_a, col_b, col_c = st.columns(3)
#                 col_a.metric("Format", image.format)
#                 col_b.metric("Size", f"{image.size[0]}x{image.size[1]}")
#                 col_c.metric("File Size", f"{len(content)/1024:.2f} KB")
                
#                 # Download button
#                 st.download_button(
#                     label="⬇️ Download Image",
#                     data=content,
#                     file_name=f"object_{obj_id}.{image.format.lower()}",
#                     mime=f"image/{image.format.lower()}",
#                     use_container_width=True
#                 )
                
#             except Exception:
#                 # Try to display as video
#                 st.video(content)
#                 st.metric("File Size", f"{len(content)/(1024*1024):.2f} MB")
                
#                 # Download button
#                 st.download_button(
#                     label="⬇️ Download Video",
#                     data=content,
#                     file_name=f"object_{obj_id}.mp4",
#                     mime="video/mp4",
#                     use_container_width=True
#                 )
        
#         # Display search results
#         if hasattr(st.session_state, 'search_results'):
#             st.divider()
#             st.subheader("Search Results")
            
#             results = st.session_state.search_results
            
#             # Display in grid
#             cols = st.columns(3)
#             for idx, obj_content in enumerate(results):
#                 with cols[idx % 3]:
#                     try:
#                         image = Image.open(io.BytesIO(obj_content))
#                         st.image(image, use_container_width=True)
#                         st.caption(f"Result {idx + 1}")
#                     except:
#                         st.info(f"Object {idx + 1} (Video)")


# def version_control_tab():
#     """Tab for version control operations"""
#     st.header("🔄 Version Control")
    
#     if not st.session_state.get('db_connected', False):
#         st.warning("⚠️ Database not connected. Please check connection.")
#         return
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("📝 Update Object")
        
#         update_name = st.text_input(
#             "Object Name",
#             key="update_name",
#             help="Name of the object to update"
#         )
        
#         media_type = st.selectbox(
#             "Media Type",
#             options=["IMAGE", "VIDEO"],
#             key="update_type"
#         )
        
#         uploaded_file = st.file_uploader(
#             "New Version File",
#             type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'] if media_type == "IMAGE" else ['mp4', 'avi', 'mov'],
#             key="update_file"
#         )
        
#         if uploaded_file:
#             if media_type == "IMAGE":
#                 image = Image.open(uploaded_file)
#                 st.image(image, caption="New Version Preview", width=300)
#             else:
#                 st.video(uploaded_file)
        
#         update_tags = st.text_input(
#             "Tags",
#             value="updated",
#             key="update_tags"
#         )
        
#         update_desc = st.text_area(
#             "Description",
#             key="update_desc"
#         )
        
#         if st.button("⬆️ Update Object", type="primary", use_container_width=True):
#             if not update_name or not uploaded_file:
#                 st.error("Please provide object name and file!")
#                 return
            
#             try:
#                 with st.spinner("Updating object..."):
#                     # Save temp file
#                     temp_path = f"temp_update_{uploaded_file.name}"
#                     with open(temp_path, "wb") as f:
#                         f.write(uploaded_file.getbuffer())
                    
#                     # Update object
#                     if media_type == "IMAGE":
#                         result = MediaStorage.update_image(
#                             name=update_name,
#                             file_path=temp_path,
#                             tags=update_tags,
#                             description=update_desc
#                         )
#                     else:
#                         result = MediaStorage.update_video(
#                             name=update_name,
#                             file_path=temp_path,
#                             tags=update_tags,
#                             description=update_desc
#                         )
                    
#                     # Clean up
#                     Path(temp_path).unlink()
                    
#                     if result:
#                         st.success("✅ Object updated successfully!")
#                     else:
#                         st.error("❌ Update failed!")
                        
#             except Exception as e:
#                 st.error(f"❌ Error updating object: {e}")
    
#     with col2:
#         st.subheader("⏮️ Rollback Object")
        
#         rollback_name = st.text_input(
#             "Object Name",
#             key="rollback_name",
#             help="Name of the object to rollback"
#         )
        
#         rollback_type = st.selectbox(
#             "Media Type",
#             options=["IMAGE", "VIDEO"],
#             key="rollback_type"
#         )
        
#         rollback_version = st.number_input(
#             "Target Version",
#             min_value=1,
#             value=1,
#             step=1,
#             key="rollback_version",
#             help="Version number to rollback to"
#         )
        
#         st.warning("""
#         ⚠️ **Warning**: Rollback will restore the object to the specified version.
#         The current version will be replaced.
#         """)
        
#         if st.button("⏮️ Rollback", type="secondary", use_container_width=True):
#             if not rollback_name:
#                 st.error("Please provide object name!")
#                 return
            
#             try:
#                 with st.spinner("Rolling back..."):
#                     result = MediaStorage.rollback_media(
#                         name=rollback_name,
#                         media_type=rollback_type,
#                         version=rollback_version
#                     )
                    
#                     if result:
#                         st.success(f"✅ Rolled back to version {rollback_version}!")
#                     else:
#                         st.error("❌ Rollback failed!")
                        
#             except Exception as e:
#                 st.error(f"❌ Error during rollback: {e}")


# def tools_tab():
#     """Tab for additional tools"""
#     st.header("🛠️ Tools")
    
#     if not st.session_state.get('db_connected', False):
#         st.warning("⚠️ Database not connected. Please check connection.")
#         return
    
#     tool_choice = st.selectbox(
#         "Select Tool",
#         options=[
#             "Create Thumbnail",
#             "Convert Format",
#             "Batch Upload",
#             "Database Stats"
#         ]
#     )
    
#     if tool_choice == "Create Thumbnail":
#         st.subheader("📐 Create Thumbnail")
        
#         source_id = st.number_input("Source Image ID", min_value=1, step=1)
#         thumb_size = st.slider("Thumbnail Size", min_value=50, max_value=500, value=150)
#         thumb_name = st.text_input("Thumbnail Name", value=f"thumbnail_{source_id}")
        
#         if st.button("Generate Thumbnail"):
#             try:
#                 with st.spinner("Creating thumbnail..."):
#                     thumb_id = create_thumbnail(
#                         object_id=source_id,
#                         size=(thumb_size, thumb_size),
#                         save_as_new=True,
#                         thumbnail_name=thumb_name
#                     )
#                     st.success(f"✅ Thumbnail created! ID: {thumb_id}")
#             except Exception as e:
#                 st.error(f"❌ Error: {e}")
    
#     elif tool_choice == "Convert Format":
#         st.subheader("🔄 Convert Image Format")
        
#         source_id = st.number_input("Source Image ID", min_value=1, step=1, key="convert_id")
#         output_format = st.selectbox("Output Format", options=["JPEG", "PNG", "WEBP"])
#         quality = st.slider("Quality", min_value=50, max_value=100, value=85)
        
#         if st.button("Convert"):
#             try:
#                 with st.spinner("Converting..."):
#                     converted = convert_image_format(
#                         object_id=source_id,
#                         output_format=output_format,
#                         quality=quality
#                     )
                    
#                     # Display result
#                     image = Image.open(io.BytesIO(converted))
#                     st.image(image, caption=f"Converted to {output_format}")
                    
#                     st.download_button(
#                         label=f"Download {output_format}",
#                         data=converted,
#                         file_name=f"converted_{source_id}.{output_format.lower()}",
#                         mime=f"image/{output_format.lower()}"
#                     )
#             except Exception as e:
#                 st.error(f"❌ Error: {e}")
    
#     elif tool_choice == "Batch Upload":
#         st.subheader("📦 Batch Upload")
#         st.info("Upload multiple files at once")
        
#         uploaded_files = st.file_uploader(
#             "Choose multiple files",
#             type=['jpg', 'jpeg', 'png', 'mp4'],
#             accept_multiple_files=True
#         )
        
#         if uploaded_files:
#             st.write(f"Selected {len(uploaded_files)} files")
            
#             if st.button("Upload All"):
#                 progress_bar = st.progress(0)
#                 status_text = st.empty()
                
#                 for idx, file in enumerate(uploaded_files):
#                     try:
#                         status_text.text(f"Uploading {file.name}...")
                        
#                         temp_path = f"temp_{file.name}"
#                         with open(temp_path, "wb") as f:
#                             f.write(file.getbuffer())
                        
#                         # Determine type
#                         ext = Path(file.name).suffix.lower()
#                         if ext in ['.jpg', '.jpeg', '.png']:
#                             MediaStorage.save_image(
#                                 file_path=temp_path,
#                                 name=Path(file.name).stem,
#                                 tags="batch_upload"
#                             )
#                         else:
#                             MediaStorage.save_video(
#                                 file_path=temp_path,
#                                 name=Path(file.name).stem,
#                                 tags="batch_upload"
#                             )
                        
#                         Path(temp_path).unlink()
                        
#                         progress_bar.progress((idx + 1) / len(uploaded_files))
                        
#                     except Exception as e:
#                         st.error(f"Error uploading {file.name}: {e}")
                
#                 status_text.text("Upload complete!")
#                 st.success(f"✅ Uploaded {len(uploaded_files)} files!")
    
#     elif tool_choice == "Database Stats":
#         st.subheader("📊 Database Statistics")
        
#         try:
#             with pool.acquire() as conn:
#                 cursor = conn.cursor()
                
#                 # Count objects
#                 cursor.execute("SELECT COUNT(*) FROM ora_lake_objects")
#                 total_objects = cursor.fetchone()[0]
                
#                 # Count by type
#                 cursor.execute("""
#                     SELECT object_type, COUNT(*) 
#                     FROM ora_lake_objects 
#                     GROUP BY object_type
#                 """)
#                 type_counts = cursor.fetchall()
                
#                 # Total storage
#                 cursor.execute("SELECT SUM(DBMS_LOB.GETLENGTH(content)) FROM ora_lake_objects")
#                 total_size = cursor.fetchone()[0] or 0
                
#                 col1, col2, col3 = st.columns(3)
#                 col1.metric("Total Objects", total_objects)
#                 col2.metric("Total Storage", f"{total_size/(1024*1024):.2f} MB")
#                 col3.metric("Object Types", len(type_counts))
                
#                 st.divider()
                
#                 st.subheader("Objects by Type")
#                 for obj_type, count in type_counts:
#                     st.write(f"**{obj_type}**: {count}")
                    
#         except Exception as e:
#             st.error(f"Error fetching stats: {e}")


# def main():
#     """Main application"""
    
#     # Initialize session state
#     if 'db_connected' not in st.session_state:
#         st.session_state.db_connected = False
    
#     # Header with connection status
#     get_connection_status()
    
#     st.divider()
    
#     # Main navigation
#     tab1, tab2, tab3, tab4, tab5 = st.tabs([
#         "📸 Upload Image",
#         "🎥 Upload Video",
#         "👁️ View Media",
#         "🔄 Version Control",
#         "🛠️ Tools"
#     ])
    
#     with tab1:
#         upload_image_tab()
    
#     with tab2:
#         upload_video_tab()
    
#     with tab3:
#         view_media_tab()
    
#     with tab4:
#         version_control_tab()
    
#     with tab5:
#         tools_tab()
    
#     # Footer
#     st.divider()
#     st.markdown("""
#     <div style='text-align: center; color: #888; padding: 1rem;'>
#         <p>OraLake Media Manager v1.0 | Built with Streamlit ❤️</p>
#     </div>
#     """, unsafe_allow_html=True)


# if __name__ == "__main__":
#     main()

####  VERSION 2 ####
# """
# OraLake Streamlit App - Media Storage Interface (UI/UX-enhanced)
# (Functional logic untouched — only UI/UX & styling updated)

# How to use:
# - Replace your current app.py with this file.
# - Run as before: streamlit run app.py
# """

# import streamlit as st
# from pathlib import Path
# import io
# from PIL import Image
# from datetime import datetime
# import json
# from typing import Optional, List
# import sys

# # Import OraLake modules
# try:
#     from src.services.media_storage import MediaStorage, create_thumbnail, convert_image_format
#     from src.services.oralake import get_object, query_by_tag
#     from src.database import pool
#     import oracledb
#     ORALAKE_AVAILABLE = True
# except ImportError as e:
#     ORALAKE_AVAILABLE = False
#     # keep same behavior (error shown) but less intrusive in layout header
#     st.error(f"⚠️ OraLake modules not available: {e}")


# # Page configuration (kept same)
# st.set_page_config(
#     page_title="OraLake Media Manager",
#     page_icon="🗄️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ---------------------------
# # THEME + BOOTSTRAP + ICONS
# # ---------------------------
# # Inject Bootstrap CSS and Bootstrap Icons CDN + custom CSS (light, formal, subtle animations)
# st.markdown(
#     """
#     <!-- Bootstrap 5 CSS -->
#     <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
#     <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">

#     <style>
#     :root{
#         --primary: #3B82F6;      /* anthracite-blue */
#         --accent: #8B5CF6;       /* violet accent */
#         --bg: #F9FAFB;
#         --card: #ffffff;
#         --muted: #6b7280;
#         --glass: rgba(255,255,255,0.6);
#         --radius: 12px;
#         --shadow: 0 6px 18px rgba(17,24,39,0.06);
#         --soft-shadow: 0 3px 10px rgba(17,24,39,0.04);
#         font-family: Inter, "Segoe UI", Roboto, system-ui, -apple-system, "Helvetica Neue", Arial;
#     }

#     /* body */
#     .stApp {
#         background-color: var(--bg);
#     }

#     /* Header area */
#     .ora-header {
#         display:flex;
#         align-items:center;
#         justify-content:space-between;
#         gap:12px;
#         padding:18px 14px;
#         background: linear-gradient(90deg, rgba(255,255,255,0.9), rgba(255,255,255,0.82));
#         border-radius: var(--radius);
#         box-shadow: var(--shadow);
#         margin-bottom: 18px;
#     }
#     .ora-title {
#         display:flex;
#         align-items:center;
#         gap:12px;
#     }
#     .ora-title h1{
#         margin:0;
#         font-size:1.4rem;
#         color: #0f172a;
#         letter-spacing: -0.2px;
#     }
#     .ora-sub {
#         color: var(--muted);
#         font-size:0.9rem;
#         margin-top:4px;
#     }

#     /* connection indicator */
#     .conn-badge {
#         display:flex;
#         align-items:center;
#         gap:8px;
#         padding:8px 12px;
#         border-radius:999px;
#         font-weight:600;
#         font-size:0.95rem;
#         box-shadow: var(--soft-shadow);
#     }
#     .conn-dot {
#         width:10px;
#         height:10px;
#         border-radius:50%;
#     }
#     .conn-connected { background: linear-gradient(90deg, #34D399, #10B981); color: #065F46; }
#     .conn-disconnected { background: linear-gradient(90deg, #FCA5A5, #FB7185); color: #7F1D1D; }

#     /* Stuff card */
#     .ora-card {
#         background: var(--card);
#         border-radius: 12px;
#         padding: 16px;
#         box-shadow: var(--soft-shadow);
#         transition: transform .18s ease, box-shadow .18s ease;
#     }
#     .ora-card:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(17,24,39,0.06); }

#     /* section headers inside cards */
#     .card-header {
#         display:flex;
#         align-items:center;
#         justify-content:space-between;
#         gap:12px;
#         margin-bottom:10px;
#     }
#     .small-title {
#         font-size:1.05rem;
#         font-weight:700;
#         color:#0f172a;
#         display:flex;
#         align-items:center;
#         gap:10px;
#     }
#     .muted-small { color:var(--muted); font-size:0.9rem; }

#     /* inputs: make them look slightly rounded */
#     .stTextInput > div, .stTextArea > div, .stNumberInput > div, .stFileUploader > div {
#         border-radius:8px !important;
#     }

#     /* buttons */
#     .btn-primary-streamlit {
#         background: linear-gradient(90deg, var(--primary), var(--accent));
#         border: none;
#         color: white;
#         border-radius: 999px;
#         padding: 8px 16px;
#         font-weight:600;
#         transition: transform .12s ease, box-shadow .12s ease;
#     }
#     .btn-primary-streamlit:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(59,130,246,0.12); }

#     /* small utility */
#     .inline-muted { color:var(--muted); font-size:0.9rem; }

#     /* grid tweak for search results images (responsive) */
#     .grid-img { border-radius:8px; box-shadow: 0 6px 18px rgba(2,6,23,0.04); }

#     /* footer */
#     .ora-footer {
#         text-align:center;
#         color:#6b7280;
#         padding:14px 0;
#         font-size:0.95rem;
#     }

#     /* subtle animation for appearing cards */
#     .fade-in { animation: fadeInUp .28s ease both; }
#     @keyframes fadeInUp {
#         from { opacity:0; transform: translateY(6px); }
#         to { opacity:1; transform: translateY(0); }
#     }

#     /* responsive adjustments */
#     @media (max-width: 900px) {
#         .ora-header { flex-direction: column; align-items:flex-start; gap:8px; }
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# # ---------------------------
# # Helper: connection check (kept logic same)
# # ---------------------------
# def check_db_connection() -> bool:
#     """Check if database connection is available"""
#     if not ORALAKE_AVAILABLE:
#         return False

#     try:
#         with pool.acquire() as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT 1 FROM DUAL")
#             result = cursor.fetchone()
#             return result is not None
#     except Exception as e:
#         st.session_state.db_error = str(e)
#         return False


# # ---------------------------
# # Header (styled)
# # ---------------------------
# def get_connection_status():
#     """Display database connection status in header (UI revamped)"""
#     # layout: left = title, middle = help/info, right = controls/status
#     cols = st.columns([3, 2, 1])
#     with cols[0]:
#         st.markdown(
#             f"""
#             <div class="ora-header fade-in">
#                 <div class="ora-title">
#                     <svg width="34" height="34" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
#                       <rect width="24" height="24" rx="6" fill="url(#g)"></rect>
#                       <defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#3B82F6"/><stop offset="1" stop-color="#8B5CF6"/></linearGradient></defs>
#                     </svg>
#                     <div>
#                         <h1>OraLake Media Manager</h1>
#                         <div class="ora-sub">Upload • View • Version • Tools — single-page media control</div>
#                     </div>
#                 </div>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )

#     with cols[1]:
#         # small helper text or status messages
#         if hasattr(st.session_state, "db_error") and st.session_state.get("db_error"):
#             st.markdown(f"<div class='inline-muted'>Last error: {st.session_state.get('db_error')}</div>", unsafe_allow_html=True)
#         else:
#             st.markdown("<div class='inline-muted'>Connected to OraLake (when status is green)</div>", unsafe_allow_html=True)

#     with cols[2]:
#         # Controls and status (Refresh stays same functionality)
#         if st.button("Refresh Connection", use_container_width=True, key="refresh_conn"):
#             st.session_state.db_connected = check_db_connection()
#             st.rerun()

#         # status indicator
#         is_connected = check_db_connection()
#         if is_connected:
#             st.session_state.db_connected = True
#             st.markdown(
#                 "<div style='display:flex;justify-content:flex-end;margin-top:8px'><div class='conn-badge conn-connected'><span class='conn-dot' style='background:#10B981'></span> Connected</div></div>",
#                 unsafe_allow_html=True,
#             )
#         else:
#             st.session_state.db_connected = False
#             st.markdown(
#                 "<div style='display:flex;justify-content:flex-end;margin-top:8px'><div class='conn-badge conn-disconnected'><span class='conn-dot' style='background:#FB7185'></span> Disconnected</div></div>",
#                 unsafe_allow_html=True,
#             )
#             if hasattr(st.session_state, 'db_error'):
#                 st.error(f"Connection Error: {st.session_state.db_error}")


# # ---------------------------
# # Tabs & card wrappers: keep existing functions but wrap in attractive cards
# # ---------------------------
# def upload_image_tab():
#     """Tab for uploading images (functionality unchanged)"""
#     # Title inside card
#     st.markdown("<div class='ora-card fade-in'>", unsafe_allow_html=True)
#     st.markdown("""
#         <div class="card-header">
#             <div class="small-title"><i class="bi bi-camera" style="font-size:1.05rem;color:var(--primary)"></i> Upload Image</div>
#             <div class="muted-small">Store images with metadata & optional compression</div>
#         </div>
#     """, unsafe_allow_html=True)

#     if not st.session_state.get('db_connected', False):
#         st.warning("⚠️ Database not connected. Please check connection.")
#         st.markdown("</div>", unsafe_allow_html=True)
#         return

#     col1, col2 = st.columns([2, 1])

#     with col1:
#         uploaded_file = st.file_uploader(
#             "Choose an image file",
#             type=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff'],
#             help="Upload an image to store in OraLake"
#         )

#         if uploaded_file:
#             # Preview image
#             image = Image.open(uploaded_file)
#             st.image(image, caption="Preview", use_container_width=True)

#             # Image info (compact)
#             st.markdown(
#                 f"<div class='inline-muted'>Filename: <strong>{uploaded_file.name}</strong> &nbsp; • &nbsp; Size: <strong>{uploaded_file.size / 1024:.2f} KB</strong> &nbsp; • &nbsp; Dimensions: <strong>{image.size[0]}x{image.size[1]}</strong> &nbsp; • &nbsp; Format: <strong>{image.format}</strong></div>",
#                 unsafe_allow_html=True,
#             )

#     with col2:
#         st.subheader("Image Settings")
#         object_name = st.text_input(
#             "Object Name",
#             value=Path(uploaded_file.name).stem if uploaded_file else "",
#             help="Unique name for this image"
#         )

#         tags = st.text_input(
#             "Tags",
#             value="image",
#             help="Comma-separated tags"
#         )

#         description = st.text_area(
#             "Description",
#             help="Optional description"
#         )

#         st.divider()

#         compress = st.checkbox("Compress Image", value=True)

#         if compress:
#             quality = st.slider(
#                 "Quality",
#                 min_value=50,
#                 max_value=100,
#                 value=85,
#                 help="JPEG quality (lower = smaller file)"
#             )
#         else:
#             quality = 95

#         max_dimension = st.number_input(
#             "Max Dimension (px)",
#             min_value=100,
#             max_value=5000,
#             value=2000,
#             step=100,
#             help="Maximum width or height"
#         )

#         st.divider()

#         # Primary action button styled
#         if st.button("Save Image", type="primary", use_container_width=True, key="save_image_btn"):
#             if not uploaded_file:
#                 st.error("Please upload an image first!")
#                 st.markdown("</div>", unsafe_allow_html=True)
#                 return

#             if not object_name:
#                 st.error("Please provide an object name!")
#                 st.markdown("</div>", unsafe_allow_html=True)
#                 return

#             try:
#                 with st.spinner("Saving image..."):
#                     # Save uploaded file temporarily
#                     temp_path = f"temp_{uploaded_file.name}"
#                     with open(temp_path, "wb") as f:
#                         f.write(uploaded_file.getbuffer())

#                     # Save to OraLake
#                     obj_id = MediaStorage.save_image(
#                         file_path=temp_path,
#                         name=object_name,
#                         tags=tags,
#                         description=description,
#                         compress=compress,
#                         quality=quality,
#                         max_dimension=max_dimension
#                     )

#                     # Clean up temp file
#                     Path(temp_path).unlink()

#                     st.success(f"Image saved successfully! ID: {obj_id}")
#                     st.balloons()

#             except Exception as e:
#                 st.error(f"Error saving image: {e}")

#     st.markdown("</div>", unsafe_allow_html=True)


# def upload_video_tab():
#     """Tab for uploading videos (functionality unchanged)"""
#     st.markdown("<div class='ora-card fade-in'>", unsafe_allow_html=True)
#     st.markdown("""
#         <div class="card-header">
#             <div class="small-title"><i class="bi bi-camera-video" style="font-size:1.05rem;color:var(--primary)"></i> Upload Video</div>
#             <div class="muted-small">Upload video files and add metadata</div>
#         </div>
#     """, unsafe_allow_html=True)

#     if not st.session_state.get('db_connected', False):
#         st.warning("⚠️ Database not connected. Please check connection.")
#         st.markdown("</div>", unsafe_allow_html=True)
#         return

#     col1, col2 = st.columns([2, 1])

#     with col1:
#         uploaded_file = st.file_uploader(
#             "Choose a video file",
#             type=['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'],
#             help="Upload a video to store in OraLake",
#             key="video_uploader"  # keep same key
#         )

#         if uploaded_file:
#             st.video(uploaded_file)
#             st.markdown(
#                 f"<div class='inline-muted'>Filename: <strong>{uploaded_file.name}</strong> &nbsp; • &nbsp; Size: <strong>{uploaded_file.size / (1024*1024):.2f} MB</strong></div>",
#                 unsafe_allow_html=True,
#             )

#     with col2:
#         st.subheader("Video Settings")
#         object_name = st.text_input(
#             "Object Name",
#             value=Path(uploaded_file.name).stem if uploaded_file else "",
#             help="Unique name for this video",
#             key="video_object_name"
#         )

#         tags = st.text_input(
#             "Tags",
#             value="video",
#             help="Comma-separated tags",
#             key="video_tags"
#         )

#         description = st.text_area(
#             "Description",
#             help="Optional description",
#             key="video_description"
#         )

#         st.divider()

#         if st.button("Save Video", type="primary", use_container_width=True, key="save_video_btn"):
#             if not uploaded_file:
#                 st.error("Please upload a video first!")
#                 st.markdown("</div>", unsafe_allow_html=True)
#                 return

#             if not object_name:
#                 st.error("Please provide an object name!")
#                 st.markdown("</div>", unsafe_allow_html=True)
#                 return

#             try:
#                 with st.spinner("Saving video..."):
#                     temp_path = f"temp_{uploaded_file.name}"
#                     with open(temp_path, "wb") as f:
#                         f.write(uploaded_file.getbuffer())

#                     obj_id = MediaStorage.save_video(
#                         file_path=temp_path,
#                         name=object_name,
#                         tags=tags,
#                         description=description
#                     )

#                     Path(temp_path).unlink()

#                     st.success(f"Video saved successfully! ID: {obj_id}")
#                     st.balloons()

#             except Exception as e:
#                 st.error(f"Error saving video: {e}")

#     st.markdown("</div>", unsafe_allow_html=True)


# def view_media_tab():
#     """Tab for viewing stored media (functionality unchanged)"""
#     st.markdown("<div class='ora-card fade-in'>", unsafe_allow_html=True)
#     st.markdown("""
#         <div class="card-header">
#             <div class="small-title"><i class="bi bi-eyeglasses" style="font-size:1.05rem;color:var(--primary)"></i> View Media</div>
#             <div class="muted-small">Retrieve by ID or search by tags</div>
#         </div>
#     """, unsafe_allow_html=True)

#     if not st.session_state.get('db_connected', False):
#         st.warning("⚠️ Database not connected. Please check connection.")
#         st.markdown("</div>", unsafe_allow_html=True)
#         return

#     col1, col2 = st.columns([1, 3])

#     with col1:
#         st.subheader("Retrieve by ID")
#         object_id = st.number_input(
#             "Object ID",
#             min_value=1,
#             step=1,
#             help="Enter the object ID to retrieve"
#         )

#         if st.button("Retrieve", use_container_width=True, key="retrieve_btn"):
#             try:
#                 with st.spinner("Retrieving..."):
#                     content = get_object(object_id)

#                     if content is None:
#                         st.error(f"Object with ID {object_id} not found!")
#                     else:
#                         st.session_state.current_object = content
#                         st.session_state.current_object_id = object_id
#                         st.success(f"Retrieved object {object_id}")

#             except Exception as e:
#                 st.error(f"Error retrieving object: {e}")

#         st.divider()
#         st.subheader("Query by Tag")
#         tag_query = st.text_input(
#             "Tag",
#             value="image",
#             help="Search for objects with this tag",
#             key="view_tag_query"
#         )

#         if st.button("Search", use_container_width=True, key="search_tag_btn"):
#             try:
#                 with st.spinner("Searching..."):
#                     objects = query_by_tag(tag_query)

#                     if objects:
#                         st.session_state.search_results = objects
#                         st.success(f"Found {len(objects)} objects")
#                     else:
#                         st.warning(f"No objects found with tag '{tag_query}'")

#             except Exception as e:
#                 st.error(f"Error searching: {e}")

#     with col2:
#         # Display current object
#         if hasattr(st.session_state, 'current_object'):
#             content = st.session_state.current_object
#             obj_id = st.session_state.current_object_id

#             st.subheader(f"Object ID: {obj_id}")

#             # Try to display as image
#             try:
#                 image = Image.open(io.BytesIO(content))
#                 st.image(image, caption=f"Object {obj_id}", use_container_width=True)

#                 # Image info
#                 col_a, col_b, col_c = st.columns(3)
#                 col_a.metric("Format", image.format)
#                 col_b.metric("Size", f"{image.size[0]}x{image.size[1]}")
#                 col_c.metric("File Size", f"{len(content)/1024:.2f} KB")

#                 # Download button
#                 st.download_button(
#                     label="Download Image",
#                     data=content,
#                     file_name=f"object_{obj_id}.{image.format.lower()}",
#                     mime=f"image/{image.format.lower()}",
#                     use_container_width=True
#                 )

#             except Exception:
#                 # Try to display as video
#                 st.video(content)
#                 st.metric("File Size", f"{len(content)/(1024*1024):.2f} MB")

#                 # Download button
#                 st.download_button(
#                     label="Download Video",
#                     data=content,
#                     file_name=f"object_{obj_id}.mp4",
#                     mime="video/mp4",
#                     use_container_width=True
#                 )

#         # Display search results
#         if hasattr(st.session_state, 'search_results'):
#             st.divider()
#             st.subheader("Search Results")
#             results = st.session_state.search_results

#             # Display in responsive grid
#             cols = st.columns(3)
#             for idx, obj_content in enumerate(results):
#                 with cols[idx % 3]:
#                     try:
#                         image = Image.open(io.BytesIO(obj_content))
#                         st.image(image, use_container_width=True, output_format="PNG")
#                         st.caption(f"Result {idx + 1}")
#                     except:
#                         st.info(f"Object {idx + 1} (Video)")

#     st.markdown("</div>", unsafe_allow_html=True)


# def version_control_tab():
#     """Tab for version control operations (functionality unchanged)"""
#     st.markdown("<div class='ora-card fade-in'>", unsafe_allow_html=True)
#     st.markdown("""
#         <div class="card-header">
#             <div class="small-title"><i class="bi bi-arrow-repeat" style="font-size:1.05rem;color:var(--primary)"></i> Version Control</div>
#             <div class="muted-small">Update or rollback media objects safely</div>
#         </div>
#     """, unsafe_allow_html=True)

#     if not st.session_state.get('db_connected', False):
#         st.warning("⚠️ Database not connected. Please check connection.")
#         st.markdown("</div>", unsafe_allow_html=True)
#         return

#     col1, col2 = st.columns(2)

#     with col1:
#         st.subheader("Update Object")
#         update_name = st.text_input(
#             "Object Name",
#             key="update_name",
#             help="Name of the object to update"
#         )

#         media_type = st.selectbox(
#             "Media Type",
#             options=["IMAGE", "VIDEO"],
#             key="update_type"
#         )

#         uploaded_file = st.file_uploader(
#             "New Version File",
#             type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'] if media_type == "IMAGE" else ['mp4', 'avi', 'mov'],
#             key="update_file"
#         )

#         if uploaded_file:
#             if media_type == "IMAGE":
#                 image = Image.open(uploaded_file)
#                 st.image(image, caption="New Version Preview", width=300)
#             else:
#                 st.video(uploaded_file)

#         update_tags = st.text_input(
#             "Tags",
#             value="updated",
#             key="update_tags"
#         )

#         update_desc = st.text_area(
#             "Description",
#             key="update_desc"
#         )

#         if st.button("Update Object", type="primary", use_container_width=True, key="update_object_btn"):
#             if not update_name or not uploaded_file:
#                 st.error("Please provide object name and file!")
#                 st.markdown("</div>", unsafe_allow_html=True)
#                 return

#             try:
#                 with st.spinner("Updating object..."):
#                     temp_path = f"temp_update_{uploaded_file.name}"
#                     with open(temp_path, "wb") as f:
#                         f.write(uploaded_file.getbuffer())

#                     if media_type == "IMAGE":
#                         result = MediaStorage.update_image(
#                             name=update_name,
#                             file_path=temp_path,
#                             tags=update_tags,
#                             description=update_desc
#                         )
#                     else:
#                         result = MediaStorage.update_video(
#                             name=update_name,
#                             file_path=temp_path,
#                             tags=update_tags,
#                             description=update_desc
#                         )

#                     Path(temp_path).unlink()

#                     if result:
#                         st.success("Object updated successfully!")
#                     else:
#                         st.error("Update failed!")

#             except Exception as e:
#                 st.error(f"Error updating object: {e}")

#     with col2:
#         st.subheader("Rollback Object")
#         rollback_name = st.text_input(
#             "Object Name",
#             key="rollback_name",
#             help="Name of the object to rollback"
#         )

#         rollback_type = st.selectbox(
#             "Media Type",
#             options=["IMAGE", "VIDEO"],
#             key="rollback_type"
#         )

#         rollback_version = st.number_input(
#             "Target Version",
#             min_value=1,
#             value=1,
#             step=1,
#             key="rollback_version",
#             help="Version number to rollback to"
#         )

#         st.warning("""
#         ⚠️ Warning: Rollback will restore the object to the specified version.
#         The current version will be replaced.
#         """)

#         if st.button("Rollback", type="secondary", use_container_width=True, key="rollback_btn"):
#             if not rollback_name:
#                 st.error("Please provide object name!")
#                 st.markdown("</div>", unsafe_allow_html=True)
#                 return

#             try:
#                 with st.spinner("Rolling back..."):
#                     result = MediaStorage.rollback_media(
#                         name=rollback_name,
#                         media_type=rollback_type,
#                         version=rollback_version
#                     )

#                     if result:
#                         st.success(f"Rolled back to version {rollback_version}!")
#                     else:
#                         st.error("Rollback failed!")

#             except Exception as e:
#                 st.error(f"Error during rollback: {e}")

#     st.markdown("</div>", unsafe_allow_html=True)


# def tools_tab():
#     """Tab for additional tools (functionality unchanged)"""
#     st.markdown("<div class='ora-card fade-in'>", unsafe_allow_html=True)
#     st.markdown("""
#         <div class="card-header">
#             <div class="small-title"><i class="bi bi-wrench" style="font-size:1.05rem;color:var(--primary)"></i> Tools</div>
#             <div class="muted-small">Thumbnails, conversion, batch uploads & DB stats</div>
#         </div>
#     """, unsafe_allow_html=True)

#     if not st.session_state.get('db_connected', False):
#         st.warning("⚠️ Database not connected. Please check connection.")
#         st.markdown("</div>", unsafe_allow_html=True)
#         return

#     tool_choice = st.selectbox(
#         "Select Tool",
#         options=[
#             "Create Thumbnail",
#             "Convert Format",
#             "Batch Upload",
#             "Database Stats"
#         ]
#     )

#     if tool_choice == "Create Thumbnail":
#         st.subheader("Create Thumbnail")
#         source_id = st.number_input("Source Image ID", min_value=1, step=1)
#         thumb_size = st.slider("Thumbnail Size", min_value=50, max_value=500, value=150)
#         thumb_name = st.text_input("Thumbnail Name", value=f"thumbnail_{source_id}")

#         if st.button("Generate Thumbnail", key="gen_thumb"):
#             try:
#                 with st.spinner("Creating thumbnail..."):
#                     thumb_id = create_thumbnail(
#                         object_id=source_id,
#                         size=(thumb_size, thumb_size),
#                         save_as_new=True,
#                         thumbnail_name=thumb_name
#                     )
#                     st.success(f"Thumbnail created! ID: {thumb_id}")
#             except Exception as e:
#                 st.error(f"Error: {e}")

#     elif tool_choice == "Convert Format":
#         st.subheader("Convert Image Format")
#         source_id = st.number_input("Source Image ID", min_value=1, step=1, key="convert_id")
#         output_format = st.selectbox("Output Format", options=["JPEG", "PNG", "WEBP"])
#         quality = st.slider("Quality", min_value=50, max_value=100, value=85)

#         if st.button("Convert", key="convert_btn"):
#             try:
#                 with st.spinner("Converting..."):
#                     converted = convert_image_format(
#                         object_id=source_id,
#                         output_format=output_format,
#                         quality=quality
#                     )

#                     image = Image.open(io.BytesIO(converted))
#                     st.image(image, caption=f"Converted to {output_format}")

#                     st.download_button(
#                         label=f"Download {output_format}",
#                         data=converted,
#                         file_name=f"converted_{source_id}.{output_format.lower()}",
#                         mime=f"image/{output_format.lower()}"
#                     )
#             except Exception as e:
#                 st.error(f"Error: {e}")

#     elif tool_choice == "Batch Upload":
#         st.subheader("Batch Upload")
#         st.info("Upload multiple files at once")

#         uploaded_files = st.file_uploader(
#             "Choose multiple files",
#             type=['jpg', 'jpeg', 'png', 'mp4'],
#             accept_multiple_files=True
#         )

#         if uploaded_files:
#             st.write(f"Selected {len(uploaded_files)} files")

#             if st.button("Upload All", key="upload_all_btn"):
#                 progress_bar = st.progress(0)
#                 status_text = st.empty()

#                 for idx, file in enumerate(uploaded_files):
#                     try:
#                         status_text.text(f"Uploading {file.name}...")

#                         temp_path = f"temp_{file.name}"
#                         with open(temp_path, "wb") as f:
#                             f.write(file.getbuffer())

#                         # Determine type
#                         ext = Path(file.name).suffix.lower()
#                         if ext in ['.jpg', '.jpeg', '.png']:
#                             MediaStorage.save_image(
#                                 file_path=temp_path,
#                                 name=Path(file.name).stem,
#                                 tags="batch_upload"
#                             )
#                         else:
#                             MediaStorage.save_video(
#                                 file_path=temp_path,
#                                 name=Path(file.name).stem,
#                                 tags="batch_upload"
#                             )

#                         Path(temp_path).unlink()

#                         progress_bar.progress((idx + 1) / len(uploaded_files))

#                     except Exception as e:
#                         st.error(f"Error uploading {file.name}: {e}")

#                 status_text.text("Upload complete!")
#                 st.success(f"Uploaded {len(uploaded_files)} files!")

#     elif tool_choice == "Database Stats":
#         st.subheader("Database Statistics")

#         try:
#             with pool.acquire() as conn:
#                 cursor = conn.cursor()

#                 # Count objects
#                 cursor.execute("SELECT COUNT(*) FROM ora_lake_objects")
#                 total_objects = cursor.fetchone()[0]

#                 # Count by type
#                 cursor.execute("""
#                     SELECT object_type, COUNT(*) 
#                     FROM ora_lake_objects 
#                     GROUP BY object_type
#                 """)
#                 type_counts = cursor.fetchall()

#                 # Total storage
#                 cursor.execute("SELECT SUM(DBMS_LOB.GETLENGTH(content)) FROM ora_lake_objects")
#                 total_size = cursor.fetchone()[0] or 0

#                 col1, col2, col3 = st.columns(3)
#                 col1.metric("Total Objects", total_objects)
#                 col2.metric("Total Storage", f"{total_size/(1024*1024):.2f} MB")
#                 col3.metric("Object Types", len(type_counts))

#                 st.divider()

#                 st.subheader("Objects by Type")
#                 for obj_type, count in type_counts:
#                     st.write(f"**{obj_type}**: {count}")

#         except Exception as e:
#             st.error(f"Error fetching stats: {e}")

#     st.markdown("</div>", unsafe_allow_html=True)


# # ---------------------------
# # MAIN (kept logic same) — single page tabs retained
# # ---------------------------
# def main():
#     """Main application"""

#     # Initialize session state
#     if 'db_connected' not in st.session_state:
#         st.session_state.db_connected = False

#     # Header with connection status
#     get_connection_status()

#     st.divider()

#     # Main navigation (tabs)
#     tab1, tab2, tab3, tab4, tab5 = st.tabs([
#         "Upload Image",
#         "Upload Video",
#         "View Media",
#         "Version Control",
#         "Tools"
#     ])

#     with tab1:
#         upload_image_tab()

#     with tab2:
#         upload_video_tab()

#     with tab3:
#         view_media_tab()

#     with tab4:
#         version_control_tab()

#     with tab5:
#         tools_tab()

#     # Footer (styled)
#     st.divider()
#     st.markdown("""
#     <div class="ora-footer">
#         OraLake Media Manager v1.0 • Built with Streamlit
#     </div>
#     """, unsafe_allow_html=True)


# if __name__ == "__main__":
#     main()



##### VERSION 3 ####

"""
OraLake Streamlit App - Anthropic-Light UI (Formal DataLake Page Designed by an Artist)
Functional logic untouched — UI/UX & styling only.
Drop-in replacement for your app.py
"""

import streamlit as st
from pathlib import Path
import io
from PIL import Image
from datetime import datetime
import json
from typing import Optional, List
import sys

# Import OraLake modules (logic unchanged)
try:
    from src.services.media_storage import MediaStorage, create_thumbnail, convert_image_format
    from src.services.oralake import get_object, query_by_tag
    from src.database import pool
    import oracledb
    ORALAKE_AVAILABLE = True
except ImportError as e:
    ORALAKE_AVAILABLE = False
    st.error(f"⚠️ OraLake modules not available: {e}")

# Keep original page config
st.set_page_config(
    page_title="OraLake Media Manager",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# Anthropic-like CSS (formal, minimal, smooth)
# -------------------------
st.markdown(
    """
    <!-- Google / Inter-ish fonts and icons -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">

    <style>
    :root{
        --bg: #fbfdff;
        --page: #f8fafc;
        --card: rgba(255,255,255,0.86);
        --text: #0f172a;
        --muted: #6b7280;
        --accent: #4f46e5; /* Claude-like soft violet-blue */
        --accent-weak: rgba(79,70,229,0.08);
        --primary: #334155;
        --radius: 14px;
        --glass-blur: 8px;
        --shadow-sm: 0 6px 18px rgba(6,11,23,0.06);
        --shadow-md: 0 18px 40px rgba(6,11,23,0.08);
        --transition: 240ms cubic-bezier(.2,.9,.25,1);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }

    html { scroll-behavior: smooth; -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale; }
    body, .stApp { background: linear-gradient(180deg, var(--page), var(--bg)); color: var(--text); }

    /* Header */
    .header-wrap {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:16px;
        padding:16px;
        border-radius:16px;
        background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8));
        box-shadow: var(--shadow-sm);
        border: 1px solid rgba(15,23,42,0.04);
        margin-bottom:18px;
    }
    .brand { display:flex; gap:14px; align-items:center; }
    .logo {
        width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center;
        background: linear-gradient(180deg, rgba(79,70,229,0.08), rgba(43,108,176,0.06));
        color: var(--accent); font-weight:700; font-size:18px;
        box-shadow: 0 6px 18px rgba(79,70,229,0.06);
    }
    .brand h1 { margin:0; font-size:1.15rem; letter-spacing:-0.2px; font-weight:600; color:var(--text); }
    .brand small { color:var(--muted); display:block; margin-top:2px; font-weight:400; }

    /* subtitle tagline under title */
    .title-tag {
        font-size:1.1rem; color:var(--muted); margin-top:6px; letter-spacing:0.2px;
    }

    /* connection badge */
    .conn {
        display:flex; gap:25px; align-items:center; padding:8px 12px; border-radius:999px; font-weight:600;
        font-size:1.1rem;
        border:1px solid rgba(15,23,42,0.03);
        background: rgba(255,255,255,0.7);
    }
    .conn .dot { width:10px; height:10px; border-radius:50%; display:inline-block; }

    /* card */
    .ora-card {
        background: var(--card);
        border-radius: var(--radius);
        padding:18px;
        box-shadow: var(--shadow-sm);
        border: 1px solid rgba(15,23,42,0.04);
        transition: transform var(--transition), box-shadow var(--transition), background var(--transition);
        backdrop-filter: blur(var(--glass-blur));
    }
    .ora-card:hover { transform: translateY(-6px); box-shadow: var(--shadow-md); }

    .section-title { display:flex; align-items:center; gap:20px; font-weight:700; font-size:1.5rem; color:var(--text); }
    .section-sub { color:var(--muted); font-size:1.25rem; margin-top:6px; }

    /* inputs slight rounding via Streamlit wrappers */
    .stTextInput > div, .stTextArea > div, .stNumberInput > div, .stFileUploader > div, .stSelectbox > div {
        border-radius:10px !important;
    }

    /* Buttons — subtle Anthropic style */
    .stButton>button {
        border-radius:999px !important;
        padding:8px 14px !important;
        font-weight:600 !important;
        transition: transform var(--transition), box-shadow var(--transition), opacity var(--transition);
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(79,70,229,0.08); }

    /* custom utility classes for consistent button look */
    .btn-primary-flat {
        background: linear-gradient(135deg, rgba(79,70,229,0.95), rgba(43,108,176,0.95));
        color: #fff !important;
        border: none !important;
    }
    .btn-secondary-soft {
        background: var(--accent-weak);
        color: var(--accent);
        border: 1px solid rgba(79,70,229,0.12) !important;
    }

    /* cards fade-in */
    .fade-card { animation: fadeIn .32s cubic-bezier(.2,.9,.25,1) both; }
    @keyframes fadeIn {
        from { opacity:0; transform: translateY(8px) scale(.995); }
        to   { opacity:1; transform: translateY(0) scale(1); }
    }

    /* grid images */
    .grid-img { border-radius:10px; box-shadow: 0 8px 22px rgba(2,6,23,0.03); }

    /* footer */
    .footer { text-align:center; color:var(--muted); padding:16px 0; font-size:0.95rem; margin-top:18px; }

    /* subtle scrollbar hide for cleaner look */
    ::-webkit-scrollbar { width:8px; height:8px; }
    ::-webkit-scrollbar-thumb { background: rgba(15,23,42,0.06); border-radius:8px; }
    ::-webkit-scrollbar-track { background: transparent; }

    /* responsive tweaks */
    @media (max-width: 880px) {
        .header-wrap { flex-direction: column; align-items:flex-start; gap:10px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Database connection check (unchanged logic)
# -------------------------
def check_db_connection() -> bool:
    """Check if database connection is available"""
    if not ORALAKE_AVAILABLE:
        return False
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        st.session_state.db_error = str(e)
        return False

# -------------------------
# Styled header (keeps refresh & logic same)
# -------------------------

def get_connection_status():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(
            """
            <div class="header-wrap fade-card" style="justify-content:center; text-align:center;">
                <div class="brand" style="flex-direction:column; align-items:center;">
                    <div class="logo"><i class="bi bi-hdd-rack-fill" style="font-size:20px"></i></div>
                    <h1 style="margin:4px 0 0 0; font-size:1.35rem; font-weight:700;">OraLake Media Manager</h1>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        # refresh button (same action)
        if st.button("Refresh", use_container_width=True, key="refresh_conn_anthropic"):
            st.session_state.db_connected = check_db_connection()
            st.rerun()

        is_connected = check_db_connection()
        if is_connected:
            st.session_state.db_connected = True
            st.markdown(
                "<div style='display:flex;justify-content:flex-end;align-items:center;gap:8px'>"
                "<div class='conn' style='background:#ECFDF5;color:#065F46;padding:8px 12px'>"
                "<span class='dot' style='background:#10B981'></span>&nbsp;Connected</div></div>",
                unsafe_allow_html=True
            )
        else:
            st.session_state.db_connected = False
            st.markdown(
                "<div style='display:flex;justify-content:flex-end;align-items:center;gap:8px'>"
                "<div class='conn' style='background:#FFF1F0;color:#7F1D1D;padding:8px 12px'>"
                "<span class='dot' style='background:#FB7185'></span>&nbsp;Disconnected</div></div>",
                unsafe_allow_html=True
            )
            if hasattr(st.session_state, 'db_error'):
                st.error(f"Connection Error: {st.session_state.db_error}")

# -------------------------
# Tab content functions — presentation only changed; logic intact
# -------------------------
def upload_image_tab():
    st.markdown("<div class='ora-card fade-card'>", unsafe_allow_html=True)
    st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div>
                <div class="section-title"><i class="bi bi-image" style="color:var(--accent)"></i>&nbsp;Upload Image</div>
                <div class="section-sub">Store images with metadata and optional compression</div>
            </div>
            <div style="color:var(--muted)">Accepted: jpg, png, webp, tiff</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get('db_connected', False):
        st.warning("⚠️ Database not connected. Please check connection.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader("Choose an image file", type=['jpg','jpeg','png','gif','bmp','webp','tiff'], help="Upload an image to store in OraLake")
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Preview", use_container_width=True)
            st.markdown(f"<div style='color:var(--muted);margin-top:6px'>Filename: <strong>{uploaded_file.name}</strong> • Size: <strong>{uploaded_file.size/1024:.2f} KB</strong> • Dimensions: <strong>{image.size[0]}x{image.size[1]}</strong></div>", unsafe_allow_html=True)

    with col2:
        st.subheader("Settings")
        object_name = st.text_input("Object Name", value=Path(uploaded_file.name).stem if uploaded_file else "", help="Unique name for this image")
        tags = st.text_input("Tags", value="image", help="Comma-separated tags")
        description = st.text_area("Description", help="Optional description")
        st.divider()
        compress = st.checkbox("Compress Image", value=True)
        if compress:
            quality = st.slider("Quality", min_value=50, max_value=100, value=85, help="JPEG quality")
        else:
            quality = 95
        max_dimension = st.number_input("Max Dimension (px)", min_value=100, max_value=5000, value=2000, step=100, help="Max width or height")
        st.divider()

        # Keep exact same action and key semantics
        if st.button("Save Image", type="primary", use_container_width=True, key="save_image_final"):
            if not uploaded_file:
                st.error("Please upload an image first!")
                st.markdown("</div>", unsafe_allow_html=True)
                return
            if not object_name:
                st.error("Please provide an object name!")
                st.markdown("</div>", unsafe_allow_html=True)
                return
            try:
                with st.spinner("Saving image..."):
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    obj_id = MediaStorage.save_image(
                        file_path=temp_path,
                        name=object_name,
                        tags=tags,
                        description=description,
                        compress=compress,
                        quality=quality,
                        max_dimension=max_dimension
                    )
                    Path(temp_path).unlink()
                    st.success(f"Image saved successfully! ID: {obj_id}")
                    st.balloons()
            except Exception as e:
                st.error(f"Error saving image: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

def upload_video_tab():
    st.markdown("<div class='ora-card fade-card'>", unsafe_allow_html=True)
    st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div>
                <div class="section-title"><i class="bi bi-camera-video" style="color:var(--accent)"></i>&nbsp;Upload Video</div>
                <div class="section-sub">Upload video files and store with metadata</div>
            </div>
            <div style="color:var(--muted)">Accepted: mp4, mov, mkv, avi</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get('db_connected', False):
        st.warning("⚠️ Database not connected. Please check connection.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader("Choose a video file", type=['mp4','avi','mov','mkv','webm','flv'], help="Upload a video to store in OraLake", key="video_uploader")
        if uploaded_file:
            st.video(uploaded_file)
            st.markdown(f"<div style='color:var(--muted);margin-top:6px'>Filename: <strong>{uploaded_file.name}</strong> • Size: <strong>{uploaded_file.size/(1024*1024):.2f} MB</strong></div>", unsafe_allow_html=True)

    with col2:
        st.subheader("Settings")
        object_name = st.text_input("Object Name", value=Path(uploaded_file.name).stem if uploaded_file else "", key="video_object_name", help="Unique name for this video")
        tags = st.text_input("Tags", value="video", key="video_tags", help="Comma-separated tags")
        description = st.text_area("Description", key="video_description", help="Optional description")
        st.divider()

        if st.button("Save Video", type="primary", use_container_width=True, key="save_video_final"):
            if not uploaded_file:
                st.error("Please upload a video first!")
                st.markdown("</div>", unsafe_allow_html=True)
                return
            if not object_name:
                st.error("Please provide an object name!")
                st.markdown("</div>", unsafe_allow_html=True)
                return
            try:
                with st.spinner("Saving video..."):
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    obj_id = MediaStorage.save_video(file_path=temp_path, name=object_name, tags=tags, description=description)
                    Path(temp_path).unlink()
                    st.success(f"Video saved successfully! ID: {obj_id}")
                    st.balloons()
            except Exception as e:
                st.error(f"Error saving video: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

def view_media_tab():
    st.markdown("<div class='ora-card fade-card'>", unsafe_allow_html=True)
    st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div>
                <div class="section-title"><i class="bi bi-search" style="color:var(--accent)"></i>&nbsp;View Media</div>
                <div class="section-sub">Retrieve by ID or search by tag. Preview and download content.</div>
            </div>
            <div style="color:var(--muted)">Preview • Download</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get('db_connected', False):
        st.warning("⚠️ Database not connected. Please check connection.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("Retrieve by ID")
        object_id = st.number_input("Object ID", min_value=1, step=1, help="Enter the object ID to retrieve")
        if st.button("Retrieve", use_container_width=True, key="retrieve_btn_simple"):
            try:
                with st.spinner("Retrieving..."):
                    content = get_object(object_id)
                    if content is None:
                        st.error(f"Object with ID {object_id} not found!")
                    else:
                        st.session_state.current_object = content
                        st.session_state.current_object_id = object_id
                        st.success(f"Retrieved object {object_id}")
            except Exception as e:
                st.error(f"Error retrieving object: {e}")

        st.divider()
        st.subheader("Query by Tag")
        tag_query = st.text_input("Tag", value="image", help="Search for objects with this tag", key="view_tag_query_simple")
        if st.button("Search", use_container_width=True, key="search_tag_btn_simple"):
            try:
                with st.spinner("Searching..."):
                    objects = query_by_tag(tag_query)
                    if objects:
                        st.session_state.search_results = objects
                        st.success(f"Found {len(objects)} objects")
                    else:
                        st.warning(f"No objects found with tag '{tag_query}'")
            except Exception as e:
                st.error(f"Error searching: {e}")

    with col2:
        if hasattr(st.session_state, 'current_object'):
            content = st.session_state.current_object
            obj_id = st.session_state.current_object_id
            st.subheader(f"Object ID: {obj_id}")
            try:
                image = Image.open(io.BytesIO(content))
                st.image(image, caption=f"Object {obj_id}", use_container_width=True)
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Format", image.format)
                col_b.metric("Size", f"{image.size[0]}x{image.size[1]}")
                col_c.metric("File Size", f"{len(content)/1024:.2f} KB")
                st.download_button(label="Download Image", data=content, file_name=f"object_{obj_id}.{image.format.lower()}", mime=f"image/{image.format.lower()}", use_container_width=True)
            except Exception:
                st.video(content)
                st.metric("File Size", f"{len(content)/(1024*1024):.2f} MB")
                st.download_button(label="Download Video", data=content, file_name=f"object_{obj_id}.mp4", mime="video/mp4", use_container_width=True)

        if hasattr(st.session_state, 'search_results'):
            st.divider()
            st.subheader("Search Results")
            results = st.session_state.search_results
            cols = st.columns(3)
            for idx, obj_content in enumerate(results):
                with cols[idx % 3]:
                    try:
                        image = Image.open(io.BytesIO(obj_content))
                        st.image(image, use_container_width=True, output_format="PNG")
                        st.caption(f"Result {idx + 1}")
                    except:
                        st.info(f"Object {idx + 1} (Video)")

    st.markdown("</div>", unsafe_allow_html=True)

def version_control_tab():
    st.markdown("<div class='ora-card fade-card'>", unsafe_allow_html=True)
    st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div>
                <div class="section-title"><i class="bi bi-arrow-repeat" style="color:var(--accent)"></i>&nbsp;Version Control</div>
                <div class="section-sub">Update object versions or rollback to previous versions</div>
            </div>
            <div style="color:var(--muted)">Safe operations</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get('db_connected', False):
        st.warning("⚠️ Database not connected. Please check connection.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Update Object")
        update_name = st.text_input("Object Name", key="update_name", help="Name of the object to update")
        media_type = st.selectbox("Media Type", options=["IMAGE", "VIDEO"], key="update_type")
        uploaded_file = st.file_uploader("New Version File", type=['jpg','jpeg','png','mp4','avi','mov'] if media_type == "IMAGE" else ['mp4','avi','mov'], key="update_file")
        if uploaded_file:
            if media_type == "IMAGE":
                image = Image.open(uploaded_file); st.image(image, caption="New Version Preview", width=300)
            else:
                st.video(uploaded_file)
        update_tags = st.text_input("Tags", value="updated", key="update_tags")
        update_desc = st.text_area("Description", key="update_desc")
        if st.button("Update Object", type="primary", use_container_width=True, key="update_object_btn_simple"):
            if not update_name or not uploaded_file:
                st.error("Please provide object name and file!")
                st.markdown("</div>", unsafe_allow_html=True)
                return
            try:
                with st.spinner("Updating object..."):
                    temp_path = f"temp_update_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    if media_type == "IMAGE":
                        result = MediaStorage.update_image(name=update_name, file_path=temp_path, tags=update_tags, description=update_desc)
                    else:
                        result = MediaStorage.update_video(name=update_name, file_path=temp_path, tags=update_tags, description=update_desc)
                    Path(temp_path).unlink()
                    if result:
                        st.success("Object updated successfully!")
                    else:
                        st.error("Update failed!")
            except Exception as e:
                st.error(f"Error updating object: {e}")

    with col2:
        st.subheader("Rollback Object")
        rollback_name = st.text_input("Object Name", key="rollback_name", help="Name of the object to rollback")
        rollback_type = st.selectbox("Media Type", options=["IMAGE", "VIDEO"], key="rollback_type")
        rollback_version = st.number_input("Target Version", min_value=1, value=1, step=1, key="rollback_version", help="Version number to rollback to")
        st.warning("⚠️ Rollback will restore the object to the specified version. The current version will be replaced.")
        if st.button("Rollback", type="secondary", use_container_width=True, key="rollback_btn_simple"):
            if not rollback_name:
                st.error("Please provide object name!")
                st.markdown("</div>", unsafe_allow_html=True)
                return
            try:
                with st.spinner("Rolling back..."):
                    result = MediaStorage.rollback_media(name=rollback_name, media_type=rollback_type, version=rollback_version)
                    if result:
                        st.success(f"Rolled back to version {rollback_version}!")
                    else:
                        st.error("Rollback failed!")
            except Exception as e:
                st.error(f"Error during rollback: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

def tools_tab():
    st.markdown("<div class='ora-card fade-card'>", unsafe_allow_html=True)
    st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div>
                <div class="section-title"><i class="bi bi-tools" style="color:var(--accent)"></i>&nbsp;Tools</div>
                <div class="section-sub">Thumbnail, convert, batch upload, DB statistics</div>
            </div>
            <div style="color:var(--muted)">Utilities</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get('db_connected', False):
        st.warning("⚠️ Database not connected. Please check connection.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    tool_choice = st.selectbox("Select Tool", options=["Create Thumbnail", "Convert Format", "Batch Upload", "Database Stats"])
    if tool_choice == "Create Thumbnail":
        st.subheader("Create Thumbnail")
        source_id = st.number_input("Source Image ID", min_value=1, step=1)
        thumb_size = st.slider("Thumbnail Size", min_value=50, max_value=500, value=150)
        thumb_name = st.text_input("Thumbnail Name", value=f"thumbnail_{source_id}")
        if st.button("Generate Thumbnail", key="gen_thumb_anthropic"):
            try:
                with st.spinner("Creating thumbnail..."):
                    thumb_id = create_thumbnail(object_id=source_id, size=(thumb_size, thumb_size), save_as_new=True, thumbnail_name=thumb_name)
                    st.success(f"Thumbnail created! ID: {thumb_id}")
            except Exception as e:
                st.error(f"Error: {e}")

    elif tool_choice == "Convert Format":
        st.subheader("Convert Image Format")
        source_id = st.number_input("Source Image ID", min_value=1, step=1, key="convert_id")
        output_format = st.selectbox("Output Format", options=["JPEG", "PNG", "WEBP"])
        quality = st.slider("Quality", min_value=50, max_value=100, value=85)
        if st.button("Convert", key="convert_btn_anthropic"):
            try:
                with st.spinner("Converting..."):
                    converted = convert_image_format(object_id=source_id, output_format=output_format, quality=quality)
                    image = Image.open(io.BytesIO(converted))
                    st.image(image, caption=f"Converted to {output_format}")
                    st.download_button(label=f"Download {output_format}", data=converted, file_name=f"converted_{source_id}.{output_format.lower()}", mime=f"image/{output_format.lower()}")
            except Exception as e:
                st.error(f"Error: {e}")

    elif tool_choice == "Batch Upload":
        st.subheader("Batch Upload")
        st.info("Upload multiple files at once")
        uploaded_files = st.file_uploader("Choose multiple files", type=['jpg','jpeg','png','mp4'], accept_multiple_files=True)
        if uploaded_files:
            st.write(f"Selected {len(uploaded_files)} files")
            if st.button("Upload All", key="upload_all_btn_anthropic"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                for idx, file in enumerate(uploaded_files):
                    try:
                        status_text.text(f"Uploading {file.name}...")
                        temp_path = f"temp_{file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(file.getbuffer())
                        ext = Path(file.name).suffix.lower()
                        if ext in ['.jpg','jpeg','.png']:
                            MediaStorage.save_image(file_path=temp_path, name=Path(file.name).stem, tags="batch_upload")
                        else:
                            MediaStorage.save_video(file_path=temp_path, name=Path(file.name).stem, tags="batch_upload")
                        Path(temp_path).unlink()
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                    except Exception as e:
                        st.error(f"Error uploading {file.name}: {e}")
                status_text.text("Upload complete!")
                st.success(f"Uploaded {len(uploaded_files)} files!")

    elif tool_choice == "Database Stats":
        st.subheader("Database Statistics")
        try:
            with pool.acquire() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM ora_lake_objects")
                total_objects = cursor.fetchone()[0]
                cursor.execute("""
                    SELECT object_type, COUNT(*) 
                    FROM ora_lake_objects 
                    GROUP BY object_type
                """)
                type_counts = cursor.fetchall()
                cursor.execute("SELECT SUM(DBMS_LOB.GETLENGTH(content)) FROM ora_lake_objects")
                total_size = cursor.fetchone()[0] or 0
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Objects", total_objects)
                col2.metric("Total Storage", f"{total_size/(1024*1024):.2f} MB")
                col3.metric("Object Types", len(type_counts))
                st.divider()
                st.subheader("Objects by Type")
                for obj_type, count in type_counts:
                    st.write(f"**{obj_type}**: {count}")
        except Exception as e:
            st.error(f"Error fetching stats: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Main — tabs retained (behavior unchanged)
# -------------------------
def main():
    if 'db_connected' not in st.session_state:
        st.session_state.db_connected = False

    get_connection_status()
    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Upload Image",
        "Upload Video",
        "View Media",
        "Version Control",
        "Tools"
    ])

    with tab1:
        upload_image_tab()
    with tab2:
        upload_video_tab()
    with tab3:
        view_media_tab()
    with tab4:
        version_control_tab()
    with tab5:
        tools_tab()

    st.divider()

if __name__ == "__main__":
    main()
