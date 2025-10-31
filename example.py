from src.services.media_storage import MediaStorage, create_thumbnail, convert_image_format
from pathlib import Path


def example_1_basic_image_storage():
    """Example 1: Basic image storage"""
    print("=" * 60)
    print("Example 1: Basic Image Storage")
    print("=" * 60)
    
    # Save an image
    obj_id = MediaStorage.save_image(
        file_path="photos/profile_pic.jpg",
        name="user_profile_john",
        tags="profile,user,photo",
        description="John's profile picture",
        compress=True,
        quality=85
    )
    
    print(f"✅ Saved image with ID: {obj_id}")
    
    # Retrieve it later
    image_bytes, metadata = MediaStorage.get_image(
        object_id=obj_id,
        save_to="downloads/profile_pic.jpg"
    )
    
    print(f"📊 Image metadata: {metadata}")
    print()


def example_2_profile_picture_updates():
    """Example 2: User updates their profile picture (version control)"""
    print("=" * 60)
    print("Example 2: Profile Picture Version Control")
    print("=" * 60)
    
    username = "alice_smith"
    
    # Initial profile picture
    obj_id = MediaStorage.save_image(
        file_path="photos/alice_v1.jpg",
        name=f"profile_{username}",
        tags="profile,user",
        description=f"{username}'s profile picture"
    )
    print(f"✅ Version 1 saved (ID: {obj_id})")
    
    # Alice updates her profile picture (Version 2)
    MediaStorage.update_image(
        name=f"profile_{username}",
        file_path="photos/alice_v2.jpg",
        tags="profile,user",
        description=f"{username}'s updated profile picture"
    )
    print(f"✅ Version 2 saved")
    
    # Another update (Version 3)
    MediaStorage.update_image(
        name=f"profile_{username}",
        file_path="photos/alice_v3.jpg",
        tags="profile,user",
        description=f"{username}'s latest profile picture"
    )
    print(f"✅ Version 3 saved")
    
    # Oops! Alice wants to go back to Version 1
    MediaStorage.rollback_media(
        name=f"profile_{username}",
        media_type='IMAGE',
        version=1
    )
    print(f"🔄 Rolled back to Version 1")
    print()


def example_3_product_images_with_thumbnails():
    """Example 3: E-commerce product images with thumbnails"""
    print("=" * 60)
    print("Example 3: Product Images with Thumbnails")
    print("=" * 60)
    
    product_id = "PROD_12345"
    
    # Save high-res product image
    obj_id = MediaStorage.save_image(
        file_path="products/laptop_highres.jpg",
        name=f"product_{product_id}_main",
        tags="product,electronics,laptop",
        description="MacBook Pro 16-inch - Main Image",
        max_dimension=2000  # Limit max size
    )
    print(f"✅ Main image saved (ID: {obj_id})")
    
    # Create thumbnail for catalog view
    thumb_id = create_thumbnail(
        object_id=obj_id,
        size=(300, 300),
        save_as_new=True,
        thumbnail_name=f"product_{product_id}_thumb"
    )
    print(f"✅ Thumbnail created (ID: {thumb_id})")
    
    # Create mini thumbnail for cart
    mini_thumb_id = create_thumbnail(
        object_id=obj_id,
        size=(100, 100),
        save_as_new=True,
        thumbnail_name=f"product_{product_id}_mini"
    )
    print(f"✅ Mini thumbnail created (ID: {mini_thumb_id})")
    print()


def example_4_video_storage():
    """Example 4: Video content storage"""
    print("=" * 60)
    print("Example 4: Video Storage")
    print("=" * 60)
    
    # Save a video tutorial
    video_id = MediaStorage.save_video(
        file_path="videos/python_tutorial.mp4",
        name="tutorial_python_basics",
        tags="tutorial,python,education",
        description="Python Basics Tutorial - Part 1"
    )
    print(f"✅ Video saved (ID: {video_id})")
    
    # Update with improved version
    MediaStorage.update_video(
        name="tutorial_python_basics",
        file_path="videos/python_tutorial_v2.mp4",
        tags="tutorial,python,education,updated",
        description="Python Basics Tutorial - Part 1 (Updated)"
    )
    print(f"✅ Video updated to Version 2")
    print()


def example_5_image_optimization_pipeline():
    """Example 5: Automated image optimization for web"""
    print("=" * 60)
    print("Example 5: Image Optimization Pipeline")
    print("=" * 60)
    
    # Original high-quality image
    original_id = MediaStorage.save_image(
        file_path="uploads/photo_original.jpg",
        name="blog_post_hero_original",
        tags="blog,original",
        compress=False  # Keep original quality
    )
    print(f"✅ Original saved (ID: {original_id})")
    
    # Web-optimized version
    web_id = MediaStorage.save_image(
        file_path="uploads/photo_original.jpg",
        name="blog_post_hero_web",
        tags="blog,web-optimized",
        compress=True,
        quality=75,
        max_dimension=1920
    )
    print(f"✅ Web version saved (ID: {web_id})")
    
    # Mobile-optimized version
    mobile_id = MediaStorage.save_image(
        file_path="uploads/photo_original.jpg",
        name="blog_post_hero_mobile",
        tags="blog,mobile-optimized",
        compress=True,
        quality=70,
        max_dimension=800
    )
    print(f"✅ Mobile version saved (ID: {mobile_id})")
    
    # Thumbnail for preview
    thumb_id = create_thumbnail(
        object_id=original_id,
        size=(200, 200),
        save_as_new=True,
        thumbnail_name="blog_post_hero_thumb"
    )
    print(f"✅ Thumbnail saved (ID: {thumb_id})")
    print()


def example_6_format_conversion():
    """Example 6: Convert images between formats"""
    print("=" * 60)
    print("Example 6: Image Format Conversion")
    print("=" * 60)
    
    # Save a PNG with transparency
    png_id = MediaStorage.save_image(
        file_path="graphics/logo.png",
        name="company_logo",
        tags="logo,branding",
        compress=False
    )
    print(f"✅ PNG logo saved (ID: {png_id})")
    
    # Convert to JPEG for email/web where transparency isn't needed
    jpeg_bytes = convert_image_format(
        object_id=png_id,
        output_format='JPEG',
        quality=90
    )
    
    # Save the converted version
    from src.services.media_storage import save_image_from_bytes
    jpeg_id = save_image_from_bytes(
        image_bytes=jpeg_bytes,
        name="company_logo_jpeg",
        tags="logo,branding,jpeg",
        description="JPEG version of company logo"
    )
    print(f"✅ Converted to JPEG (ID: {jpeg_id})")
    print()


def example_7_document_scanning_workflow():
    """Example 7: Document scanning with version history"""
    print("=" * 60)
    print("Example 7: Document Scanning Workflow")
    print("=" * 60)
    
    doc_name = "invoice_2025_001"
    
    # Initial scan (maybe not perfect)
    scan_id = MediaStorage.save_image(
        file_path="scans/invoice_scan1.jpg",
        name=doc_name,
        tags="invoice,document,scan",
        description="Invoice #001 - Initial Scan"
    )
    print(f"✅ Initial scan saved (ID: {scan_id})")
    
    # Re-scan with better quality
    MediaStorage.update_image(
        name=doc_name,
        file_path="scans/invoice_scan2.jpg",
        tags="invoice,document,scan,improved",
        description="Invoice #001 - Improved Scan"
    )
    print(f"✅ Improved scan saved (Version 2)")
    
    # Final processed version (enhanced, cropped, etc.)
    MediaStorage.update_image(
        name=doc_name,
        file_path="scans/invoice_final.jpg",
        tags="invoice,document,scan,final",
        description="Invoice #001 - Final Processed"
    )
    print(f"✅ Final version saved (Version 3)")
    
    # If something went wrong, can always rollback
    # MediaStorage.rollback_media(doc_name, 'IMAGE', 2)
    print()


def example_8_batch_upload_photos():
    """Example 8: Batch upload event photos"""
    print("=" * 60)
    print("Example 8: Batch Upload Event Photos")
    print("=" * 60)
    
    event_name = "company_party_2025"
    photo_folder = Path("events/company_party/")
    
    uploaded_ids = []
    
    # Simulate batch upload
    photo_files = [
        "photo1.jpg", "photo2.jpg", "photo3.jpg",
        "photo4.jpg", "photo5.jpg"
    ]
    
    for i, photo_file in enumerate(photo_files, 1):
        obj_id = MediaStorage.save_image(
            file_path=str(photo_folder / photo_file),
            name=f"{event_name}_photo_{i:03d}",
            tags=f"event,party,{event_name}",
            description=f"Company Party 2025 - Photo {i}",
            compress=True,
            quality=80,
            max_dimension=1920
        )
        uploaded_ids.append(obj_id)
        print(f"✅ Photo {i}/5 uploaded (ID: {obj_id})")
    
    print(f"\n📸 Total photos uploaded: {len(uploaded_ids)}")
    print()


# Run all examples
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Media Storage Examples - Version Control Demo")
    print("=" * 60 + "\n")
    
    try:
        example_1_basic_image_storage()
        example_2_profile_picture_updates()
        example_3_product_images_with_thumbnails()
        example_4_video_storage()
        example_5_image_optimization_pipeline()
        example_6_format_conversion()
        example_7_document_scanning_workflow()
        example_8_batch_upload_photos()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")