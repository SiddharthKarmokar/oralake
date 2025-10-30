import pytest
from src.services.oralake import add_object, get_object, update_object, rollback_object
from src.database import pool

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data before each test"""
    yield  # Run the test first
    
    # Cleanup after test
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            # Delete test objects and their related data
            cursor.execute("""
                DELETE FROM ora_lake_versions 
                WHERE object_id IN (
                    SELECT object_id FROM ora_lake_objects 
                    WHERE object_name = 'test_version_user'
                )
            """)
            cursor.execute("""
                DELETE FROM ora_lake_metadata 
                WHERE object_id IN (
                    SELECT object_id FROM ora_lake_objects 
                    WHERE object_name = 'test_version_user'
                )
            """)
            cursor.execute("""
                DELETE FROM ora_lake_objects 
                WHERE object_name = 'test_version_user'
            """)
            conn.commit()
    except Exception as e:
        print(f"Cleanup error: {e}")

@pytest.mark.integration
def test_update_and_rollback_object():
    # Step 1️⃣: Create initial object
    content_v1 = b'{"user": "Alice", "role": "viewer"}'
    name = "test_version_user"
    obj_type = "JSON"
    tags = "versioning,test"
    description = "Initial version for rollback test"

    obj_id = add_object(
        name=name,
        obj_type=obj_type,
        content=content_v1,
        tags=tags,
        description=description
    )

    assert isinstance(obj_id, int), "Object creation failed — invalid ID"
    original_content = get_object(obj_id)
    assert b"Alice" in original_content

    # Step 2️⃣: Update to Version 2
    content_v2 = b'{"user": "Alice", "role": "editor"}'
    assert update_object(name, obj_type, content_v2, tags, "Updated to editor role")

    updated_content = get_object(obj_id)
    assert b"editor" in updated_content
    assert b"viewer" not in updated_content

    # Step 3️⃣: Update to Version 3
    content_v3 = b'{"user": "Alice", "role": "admin"}'
    assert update_object(name, obj_type, content_v3, tags, "Updated to admin role")

    latest_content = get_object(obj_id)
    assert b"admin" in latest_content

    # Step 4️⃣: Rollback to Version 1
    assert rollback_object(name, obj_type, 1) is True

    rolled_back_content = get_object(obj_id)
    assert b"viewer" in rolled_back_content, "Rollback did not revert to version 1"
    assert b"admin" not in rolled_back_content

    print("\n✅ Version control and rollback test passed successfully!")

if __name__ == "__main__":
    pytest.main(["-v", __file__])
