"""
Tests for Media Storage with Version Control
"""

import pytest
from pathlib import Path
import io
from PIL import Image
from src.services.media_storage import (
    MediaStorage, 
    save_image_from_bytes,
    convert_image_format,
    create_thumbnail
)
from src.database import pool


@pytest.fixture(autouse=True)
def cleanup_test_media():
    """Clean up test media before and after each test"""
    # Cleanup BEFORE test
    _cleanup()
    
    yield
    
    # Cleanup AFTER test
    _cleanup()


def _cleanup():
    """Helper function to clean up test data"""
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            
            # Delete test media objects (order matters due to foreign keys)
            test_patterns = [
                'test_%',
                'thumbnail_%'
            ]
            
            for pattern in test_patterns:
                # Delete versions first
                cursor.execute("""
                    DELETE FROM ora_lake_versions 
                    WHERE object_id IN (
                        SELECT object_id FROM ora_lake_objects 
                        WHERE object_name LIKE :pattern
                    )
                """, pattern=pattern)
                
                # Delete metadata
                cursor.execute("""
                    DELETE FROM ora_lake_metadata 
                    WHERE object_id IN (
                        SELECT object_id FROM ora_lake_objects 
                        WHERE object_name LIKE :pattern
                    )
                """, pattern=pattern)
                
                # Delete objects
                cursor.execute("""
                    DELETE FROM ora_lake_objects 
                    WHERE object_name LIKE :pattern
                """, pattern=pattern)
            
            conn.commit()
    except Exception as e:
        print(f"Cleanup error: {e}")


def create_test_image(filename: str, size=(800, 600), color='red'):
    """Helper to create a test image"""
    img = Image.new('RGB', size, color=color)
    img.save(filename, 'JPEG')
    return filename


def create_test_video(filename: str, size_kb=100):
    """Helper to create a dummy test video file"""
    with open(filename, 'wb') as f:
        f.write(b'\x00' * (size_kb * 1024))
    return filename


@pytest.mark.integration
def test_save_and_retrieve_image(tmp_path):
    """Test saving and retrieving an image"""
    # Create test image
    test_img = tmp_path / "test_image.jpg"
    create_test_image(str(test_img), size=(800, 600), color='blue')
    
    # Save to OraLake
    obj_id = MediaStorage.save_image(
        file_path=str(test_img),
        name="test_image_media",
        tags="test,image,blue",
        description="Test image for storage",
        compress=True,
        quality=85
    )
    
    assert isinstance(obj_id, int), "Failed to save image"
    
    # Retrieve the image
    output_path = tmp_path / "retrieved_image.jpg"
    image_bytes, metadata = MediaStorage.get_image(obj_id, save_to=str(output_path))
    
    assert output_path.exists(), "Image was not saved to disk"
    assert metadata['format'] == 'JPEG'
    assert metadata['size'] == (800, 600)
    
    print(f"✅ Image saved with ID {obj_id} and retrieved successfully")


@pytest.mark.integration
def test_image_version_control(tmp_path):
    """Test image versioning and rollback"""
    name = "test_versioned_media"
    
    # Version 1: Red image
    v1_img = tmp_path / "v1.jpg"
    create_test_image(str(v1_img), size=(400, 300), color='red')
    
    obj_id = MediaStorage.save_image(
        file_path=str(v1_img),
        name=name,
        tags="test,versioned",
        description="Version 1 - Red"
    )
    
    # Version 2: Green image
    v2_img = tmp_path / "v2.jpg"
    create_test_image(str(v2_img), size=(400, 300), color='green')
    
    result = MediaStorage.update_image(
        name=name,
        file_path=str(v2_img),
        tags="test,versioned",
        description="Version 2 - Green"
    )
    assert result is True
    
    # Version 3: Blue image
    v3_img = tmp_path / "v3.jpg"
    create_test_image(str(v3_img), size=(400, 300), color='blue')
    
    result = MediaStorage.update_image(
        name=name,
        file_path=str(v3_img),
        tags="test,versioned",
        description="Version 3 - Blue"
    )
    assert result is True
    
    # Current should be blue (allow for JPEG compression artifacts)
    current_bytes, _ = MediaStorage.get_image(obj_id)
    current_img = Image.open(io.BytesIO(current_bytes))
    current_color = current_img.getpixel((0, 0))
    # JPEG compression may cause slight color variations
    assert current_color[2] > 250, "Current version should be blue"
    assert current_color[0] < 5 and current_color[1] < 5, "Should not have red or green"
    
    # Rollback to version 1 (red)
    rollback_result = MediaStorage.rollback_media(name, 'IMAGE', 1)
    assert rollback_result is True
    
    # Verify rollback (allow for JPEG compression)
    rolled_back_bytes, _ = MediaStorage.get_image(obj_id)
    rolled_back_img = Image.open(io.BytesIO(rolled_back_bytes))
    rolled_back_color = rolled_back_img.getpixel((0, 0))
    # Should be red (255, 0, 0) but allow for compression
    assert rolled_back_color[0] > 250, "Should be rolled back to red"
    assert rolled_back_color[1] < 5 and rolled_back_color[2] < 5, "Should not have green or blue"
    
    print(f"✅ Image version control test passed!")


@pytest.mark.integration
def test_image_compression_and_resize(tmp_path):
    """Test image compression and resizing"""
    # Create large test image
    large_img = tmp_path / "large.jpg"
    create_test_image(str(large_img), size=(2000, 1500), color='purple')
    
    original_size = Path(large_img).stat().st_size
    
    # Save with compression and max dimension
    obj_id = MediaStorage.save_image(
        file_path=str(large_img),
        name="test_compressed_media",
        compress=True,
        quality=70,
        max_dimension=800
    )
    
    # Retrieve and check
    img_bytes, metadata = MediaStorage.get_image(obj_id)
    
    # Should be resized
    assert max(metadata['size']) <= 800, "Image not properly resized"
    # Should be compressed
    assert len(img_bytes) < original_size, "Image not compressed"
    
    print(f"✅ Compression test: {original_size} bytes → {len(img_bytes)} bytes")


@pytest.mark.integration
def test_save_video(tmp_path):
    """Test saving and retrieving a video"""
    # Create dummy video file
    test_video = tmp_path / "test_video.mp4"
    create_test_video(str(test_video), size_kb=50)
    
    # Save to OraLake
    obj_id = MediaStorage.save_video(
        file_path=str(test_video),
        name="test_sample_video",
        tags="test,video,mp4",
        description="Test video for storage"
    )
    
    assert isinstance(obj_id, int), "Failed to save video"
    
    # Retrieve the video
    output_path = tmp_path / "retrieved_video.mp4"
    video_bytes, metadata = MediaStorage.get_video(obj_id, save_to=str(output_path))
    
    assert output_path.exists(), "Video was not saved to disk"
    assert metadata['file_size_bytes'] == 50 * 1024
    
    print(f"✅ Video saved with ID {obj_id} and retrieved successfully")


@pytest.mark.integration
def test_create_thumbnail(tmp_path):
    """Test thumbnail creation"""
    # Create test image
    test_img = tmp_path / "original.jpg"
    create_test_image(str(test_img), size=(1200, 900), color='orange')
    
    # Save original
    obj_id = MediaStorage.save_image(
        file_path=str(test_img),
        name="test_thumbnail_source",
        tags="test,original"
    )
    
    # Create thumbnail
    thumb_id = create_thumbnail(
        object_id=obj_id,
        size=(150, 150),
        save_as_new=True,
        thumbnail_name="test_thumbnail_150"
    )
    
    # Verify thumbnail
    thumb_bytes, thumb_metadata = MediaStorage.get_image(thumb_id)
    assert max(thumb_metadata['size']) <= 150, "Thumbnail too large"
    
    print(f"✅ Thumbnail created: {thumb_metadata['size']}")


@pytest.mark.integration
def test_convert_image_format(tmp_path):
    """Test image format conversion"""
    # Create PNG with transparency
    png_img = tmp_path / "test.png"
    img = Image.new('RGBA', (200, 200), color=(255, 0, 0, 128))
    img.save(str(png_img), 'PNG')
    
    # Save as PNG
    obj_id = MediaStorage.save_image(
        file_path=str(png_img),
        name="test_format_convert",
        compress=False
    )
    
    # Convert to JPEG
    jpeg_bytes = convert_image_format(obj_id, output_format='JPEG', quality=90)
    
    # Verify conversion
    converted_img = Image.open(io.BytesIO(jpeg_bytes))
    assert converted_img.format == 'JPEG'
    assert converted_img.mode == 'RGB', "Should be converted to RGB"
    
    print(f"✅ Format conversion: PNG → JPEG")


@pytest.mark.integration
def test_save_image_from_bytes():
    """Test saving image directly from bytes"""
    # Create image in memory
    img = Image.new('RGB', (300, 300), color='cyan')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    image_bytes = buffer.getvalue()
    
    # Save from bytes
    obj_id = save_image_from_bytes(
        image_bytes=image_bytes,
        name="test_from_bytes",
        tags="test,memory",
        description="Image created from bytes"
    )
    
    assert isinstance(obj_id, int)
    print(f"✅ Image saved from bytes with ID {obj_id}")


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])