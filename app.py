"""
OraLake Streamlit App - Media Storage Interface
Interactive UI for managing images and videos with version control
"""

import streamlit as st
from pathlib import Path
import io
from PIL import Image
from datetime import datetime
import json
from typing import Optional, List
import sys

# Import OraLake modules
try:
    from src.services.media_storage import MediaStorage, create_thumbnail, convert_image_format
    from src.services.oralake import get_object, query_by_tag
    from src.database import pool
    import oracledb
    ORALAKE_AVAILABLE = True
except ImportError as e:
    ORALAKE_AVAILABLE = False
    st.error(f"⚠️ OraLake modules not available: {e}")


# Page configuration
st.set_page_config(
    page_title="OraLake Media Manager",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .status-connected {
        color: #28a745;
        font-weight: bold;
    }
    .status-disconnected {
        color: #dc3545;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .version-badge {
        background-color: #007bff;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


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


def get_connection_status():
    """Display database connection status in header"""
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown('<div class="main-header">🗄️ OraLake Media Manager</div>', 
                   unsafe_allow_html=True)
    
    with col2:
        if st.button("🔄 Refresh Connection", use_container_width=True):
            st.session_state.db_connected = check_db_connection()
            st.rerun()
    
    with col3:
        is_connected = check_db_connection()
        if is_connected:
            st.markdown(
                '<div class="status-connected">🟢 Connected</div>', 
                unsafe_allow_html=True
            )
            st.session_state.db_connected = True
        else:
            st.markdown(
                '<div class="status-disconnected">🔴 Disconnected</div>', 
                unsafe_allow_html=True
            )
            st.session_state.db_connected = False
            if hasattr(st.session_state, 'db_error'):
                st.error(f"Connection Error: {st.session_state.db_error}")


def upload_image_tab():
    """Tab for uploading images"""
    st.header("📸 Upload Image")
    
    if not st.session_state.get('db_connected', False):
        st.warning("⚠️ Database not connected. Please check connection.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff'],
            help="Upload an image to store in OraLake"
        )
        
        if uploaded_file:
            # Preview image
            image = Image.open(uploaded_file)
            st.image(image, caption="Preview", use_container_width=True)
            
            # Image info
            st.info(f"""
            **Filename:** {uploaded_file.name}  
            **Size:** {uploaded_file.size / 1024:.2f} KB  
            **Dimensions:** {image.size[0]} x {image.size[1]} px  
            **Format:** {image.format}
            """)
    
    with col2:
        st.subheader("Image Settings")
        
        object_name = st.text_input(
            "Object Name",
            value=Path(uploaded_file.name).stem if uploaded_file else "",
            help="Unique name for this image"
        )
        
        tags = st.text_input(
            "Tags",
            value="image",
            help="Comma-separated tags"
        )
        
        description = st.text_area(
            "Description",
            help="Optional description"
        )
        
        st.divider()
        
        compress = st.checkbox("Compress Image", value=True)
        
        if compress:
            quality = st.slider(
                "Quality",
                min_value=50,
                max_value=100,
                value=85,
                help="JPEG quality (lower = smaller file)"
            )
        else:
            quality = 95
        
        max_dimension = st.number_input(
            "Max Dimension (px)",
            min_value=100,
            max_value=5000,
            value=2000,
            step=100,
            help="Maximum width or height"
        )
        
        st.divider()
        
        if st.button("💾 Save Image", type="primary", use_container_width=True):
            if not uploaded_file:
                st.error("Please upload an image first!")
                return
            
            if not object_name:
                st.error("Please provide an object name!")
                return
            
            try:
                with st.spinner("Saving image..."):
                    # Save uploaded file temporarily
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Save to OraLake
                    obj_id = MediaStorage.save_image(
                        file_path=temp_path,
                        name=object_name,
                        tags=tags,
                        description=description,
                        compress=compress,
                        quality=quality,
                        max_dimension=max_dimension
                    )
                    
                    # Clean up temp file
                    Path(temp_path).unlink()
                    
                    st.success(f"✅ Image saved successfully! ID: {obj_id}")
                    st.balloons()
                    
            except Exception as e:
                st.error(f"❌ Error saving image: {e}")

def upload_video_tab():
    """Tab for uploading videos"""
    st.header("🎥 Upload Video")
    
    if not st.session_state.get('db_connected', False):
        st.warning("⚠️ Database not connected. Please check connection.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'],
            help="Upload a video to store in OraLake",
            key="video_uploader"  # Added unique key
        )
        
        if uploaded_file:
            st.video(uploaded_file)
            
            st.info(f"""
            **Filename:** {uploaded_file.name}  
            **Size:** {uploaded_file.size / (1024*1024):.2f} MB
            """)
    
    with col2:
        st.subheader("Video Settings")
        
        object_name = st.text_input(
            "Object Name",
            value=Path(uploaded_file.name).stem if uploaded_file else "",
            help="Unique name for this video",
            key="video_object_name"  # Added unique key
        )
        
        tags = st.text_input(
            "Tags",
            value="video",
            help="Comma-separated tags",
            key="video_tags"  # Added unique key
        )
        
        description = st.text_area(
            "Description",
            help="Optional description",
            key="video_description"  # Added unique key - THIS WAS MISSING
        )
        
        st.divider()
        
        if st.button("💾 Save Video", type="primary", use_container_width=True, key="save_video_btn"):
            if not uploaded_file:
                st.error("Please upload a video first!")
                return
            
            if not object_name:
                st.error("Please provide an object name!")
                return
            
            try:
                with st.spinner("Saving video..."):
                    # Save uploaded file temporarily
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Save to OraLake
                    obj_id = MediaStorage.save_video(
                        file_path=temp_path,
                        name=object_name,
                        tags=tags,
                        description=description
                    )
                    
                    # Clean up temp file
                    Path(temp_path).unlink()
                    
                    st.success(f"✅ Video saved successfully! ID: {obj_id}")
                    st.balloons()
                    
            except Exception as e:
                st.error(f"❌ Error saving video: {e}")

def view_media_tab():
    """Tab for viewing stored media"""
    st.header("👁️ View Media")
    
    if not st.session_state.get('db_connected', False):
        st.warning("⚠️ Database not connected. Please check connection.")
        return
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Retrieve by ID")
        
        object_id = st.number_input(
            "Object ID",
            min_value=1,
            step=1,
            help="Enter the object ID to retrieve"
        )
        
        if st.button("🔍 Retrieve", use_container_width=True):
            try:
                with st.spinner("Retrieving..."):
                    content = get_object(object_id)
                    
                    if content is None:
                        st.error(f"Object with ID {object_id} not found!")
                    else:
                        st.session_state.current_object = content
                        st.session_state.current_object_id = object_id
                        st.success(f"✅ Retrieved object {object_id}")
                        
            except Exception as e:
                st.error(f"❌ Error retrieving object: {e}")
        
        st.divider()
        
        st.subheader("Query by Tag")
        
        tag_query = st.text_input(
            "Tag",
            value="image",
            help="Search for objects with this tag"
        )
        
        if st.button("🔎 Search", use_container_width=True):
            try:
                with st.spinner("Searching..."):
                    objects = query_by_tag(tag_query)
                    
                    if objects:
                        st.session_state.search_results = objects
                        st.success(f"✅ Found {len(objects)} objects")
                    else:
                        st.warning(f"No objects found with tag '{tag_query}'")
                        
            except Exception as e:
                st.error(f"❌ Error searching: {e}")
    
    with col2:
        # Display current object
        if hasattr(st.session_state, 'current_object'):
            content = st.session_state.current_object
            obj_id = st.session_state.current_object_id
            
            st.subheader(f"Object ID: {obj_id}")
            
            # Try to display as image
            try:
                image = Image.open(io.BytesIO(content))
                st.image(image, caption=f"Object {obj_id}", use_container_width=True)
                
                # Image info
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Format", image.format)
                col_b.metric("Size", f"{image.size[0]}x{image.size[1]}")
                col_c.metric("File Size", f"{len(content)/1024:.2f} KB")
                
                # Download button
                st.download_button(
                    label="⬇️ Download Image",
                    data=content,
                    file_name=f"object_{obj_id}.{image.format.lower()}",
                    mime=f"image/{image.format.lower()}",
                    use_container_width=True
                )
                
            except Exception:
                # Try to display as video
                st.video(content)
                st.metric("File Size", f"{len(content)/(1024*1024):.2f} MB")
                
                # Download button
                st.download_button(
                    label="⬇️ Download Video",
                    data=content,
                    file_name=f"object_{obj_id}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
        
        # Display search results
        if hasattr(st.session_state, 'search_results'):
            st.divider()
            st.subheader("Search Results")
            
            results = st.session_state.search_results
            
            # Display in grid
            cols = st.columns(3)
            for idx, obj_content in enumerate(results):
                with cols[idx % 3]:
                    try:
                        image = Image.open(io.BytesIO(obj_content))
                        st.image(image, use_container_width=True)
                        st.caption(f"Result {idx + 1}")
                    except:
                        st.info(f"Object {idx + 1} (Video)")


def version_control_tab():
    """Tab for version control operations"""
    st.header("🔄 Version Control")
    
    if not st.session_state.get('db_connected', False):
        st.warning("⚠️ Database not connected. Please check connection.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Update Object")
        
        update_name = st.text_input(
            "Object Name",
            key="update_name",
            help="Name of the object to update"
        )
        
        media_type = st.selectbox(
            "Media Type",
            options=["IMAGE", "VIDEO"],
            key="update_type"
        )
        
        uploaded_file = st.file_uploader(
            "New Version File",
            type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'] if media_type == "IMAGE" else ['mp4', 'avi', 'mov'],
            key="update_file"
        )
        
        if uploaded_file:
            if media_type == "IMAGE":
                image = Image.open(uploaded_file)
                st.image(image, caption="New Version Preview", width=300)
            else:
                st.video(uploaded_file)
        
        update_tags = st.text_input(
            "Tags",
            value="updated",
            key="update_tags"
        )
        
        update_desc = st.text_area(
            "Description",
            key="update_desc"
        )
        
        if st.button("⬆️ Update Object", type="primary", use_container_width=True):
            if not update_name or not uploaded_file:
                st.error("Please provide object name and file!")
                return
            
            try:
                with st.spinner("Updating object..."):
                    # Save temp file
                    temp_path = f"temp_update_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Update object
                    if media_type == "IMAGE":
                        result = MediaStorage.update_image(
                            name=update_name,
                            file_path=temp_path,
                            tags=update_tags,
                            description=update_desc
                        )
                    else:
                        result = MediaStorage.update_video(
                            name=update_name,
                            file_path=temp_path,
                            tags=update_tags,
                            description=update_desc
                        )
                    
                    # Clean up
                    Path(temp_path).unlink()
                    
                    if result:
                        st.success("✅ Object updated successfully!")
                    else:
                        st.error("❌ Update failed!")
                        
            except Exception as e:
                st.error(f"❌ Error updating object: {e}")
    
    with col2:
        st.subheader("⏮️ Rollback Object")
        
        rollback_name = st.text_input(
            "Object Name",
            key="rollback_name",
            help="Name of the object to rollback"
        )
        
        rollback_type = st.selectbox(
            "Media Type",
            options=["IMAGE", "VIDEO"],
            key="rollback_type"
        )
        
        rollback_version = st.number_input(
            "Target Version",
            min_value=1,
            value=1,
            step=1,
            key="rollback_version",
            help="Version number to rollback to"
        )
        
        st.warning("""
        ⚠️ **Warning**: Rollback will restore the object to the specified version.
        The current version will be replaced.
        """)
        
        if st.button("⏮️ Rollback", type="secondary", use_container_width=True):
            if not rollback_name:
                st.error("Please provide object name!")
                return
            
            try:
                with st.spinner("Rolling back..."):
                    result = MediaStorage.rollback_media(
                        name=rollback_name,
                        media_type=rollback_type,
                        version=rollback_version
                    )
                    
                    if result:
                        st.success(f"✅ Rolled back to version {rollback_version}!")
                    else:
                        st.error("❌ Rollback failed!")
                        
            except Exception as e:
                st.error(f"❌ Error during rollback: {e}")


def tools_tab():
    """Tab for additional tools"""
    st.header("🛠️ Tools")
    
    if not st.session_state.get('db_connected', False):
        st.warning("⚠️ Database not connected. Please check connection.")
        return
    
    tool_choice = st.selectbox(
        "Select Tool",
        options=[
            "Create Thumbnail",
            "Convert Format",
            "Batch Upload",
            "Database Stats"
        ]
    )
    
    if tool_choice == "Create Thumbnail":
        st.subheader("📐 Create Thumbnail")
        
        source_id = st.number_input("Source Image ID", min_value=1, step=1)
        thumb_size = st.slider("Thumbnail Size", min_value=50, max_value=500, value=150)
        thumb_name = st.text_input("Thumbnail Name", value=f"thumbnail_{source_id}")
        
        if st.button("Generate Thumbnail"):
            try:
                with st.spinner("Creating thumbnail..."):
                    thumb_id = create_thumbnail(
                        object_id=source_id,
                        size=(thumb_size, thumb_size),
                        save_as_new=True,
                        thumbnail_name=thumb_name
                    )
                    st.success(f"✅ Thumbnail created! ID: {thumb_id}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    elif tool_choice == "Convert Format":
        st.subheader("🔄 Convert Image Format")
        
        source_id = st.number_input("Source Image ID", min_value=1, step=1, key="convert_id")
        output_format = st.selectbox("Output Format", options=["JPEG", "PNG", "WEBP"])
        quality = st.slider("Quality", min_value=50, max_value=100, value=85)
        
        if st.button("Convert"):
            try:
                with st.spinner("Converting..."):
                    converted = convert_image_format(
                        object_id=source_id,
                        output_format=output_format,
                        quality=quality
                    )
                    
                    # Display result
                    image = Image.open(io.BytesIO(converted))
                    st.image(image, caption=f"Converted to {output_format}")
                    
                    st.download_button(
                        label=f"Download {output_format}",
                        data=converted,
                        file_name=f"converted_{source_id}.{output_format.lower()}",
                        mime=f"image/{output_format.lower()}"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    elif tool_choice == "Batch Upload":
        st.subheader("📦 Batch Upload")
        st.info("Upload multiple files at once")
        
        uploaded_files = st.file_uploader(
            "Choose multiple files",
            type=['jpg', 'jpeg', 'png', 'mp4'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.write(f"Selected {len(uploaded_files)} files")
            
            if st.button("Upload All"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, file in enumerate(uploaded_files):
                    try:
                        status_text.text(f"Uploading {file.name}...")
                        
                        temp_path = f"temp_{file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(file.getbuffer())
                        
                        # Determine type
                        ext = Path(file.name).suffix.lower()
                        if ext in ['.jpg', '.jpeg', '.png']:
                            MediaStorage.save_image(
                                file_path=temp_path,
                                name=Path(file.name).stem,
                                tags="batch_upload"
                            )
                        else:
                            MediaStorage.save_video(
                                file_path=temp_path,
                                name=Path(file.name).stem,
                                tags="batch_upload"
                            )
                        
                        Path(temp_path).unlink()
                        
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                        
                    except Exception as e:
                        st.error(f"Error uploading {file.name}: {e}")
                
                status_text.text("Upload complete!")
                st.success(f"✅ Uploaded {len(uploaded_files)} files!")
    
    elif tool_choice == "Database Stats":
        st.subheader("📊 Database Statistics")
        
        try:
            with pool.acquire() as conn:
                cursor = conn.cursor()
                
                # Count objects
                cursor.execute("SELECT COUNT(*) FROM ora_lake_objects")
                total_objects = cursor.fetchone()[0]
                
                # Count by type
                cursor.execute("""
                    SELECT object_type, COUNT(*) 
                    FROM ora_lake_objects 
                    GROUP BY object_type
                """)
                type_counts = cursor.fetchall()
                
                # Total storage
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


def main():
    """Main application"""
    
    # Initialize session state
    if 'db_connected' not in st.session_state:
        st.session_state.db_connected = False
    
    # Header with connection status
    get_connection_status()
    
    st.divider()
    
    # Main navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📸 Upload Image",
        "🎥 Upload Video",
        "👁️ View Media",
        "🔄 Version Control",
        "🛠️ Tools"
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
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #888; padding: 1rem;'>
        <p>OraLake Media Manager v1.0 | Built with Streamlit ❤️</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()