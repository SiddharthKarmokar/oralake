from src.services.ora_lake import add_object, get_object, tag_object, query_by_tag
import pytest

@pytest.mark.integration
def test_add_get_object(monkeypatch):
    content = b'{"name": "Alice", "age":25}'
    obj_id = add_object(
        name="user_1",
        obj_type="JSON",
        content=content,
        tags="demo,json",
        description="Test JSON file"
    )

    assert isinstance(obj_id, int), "Returned ID must be integer"

    fetched = get_object(obj_id)
    assert isinstance(fetched, (bytes, bytearray))
    assert b"Bob" in fetched

@pytest.mark.integration
def test_tag_object():
    content = b'{"city": "Delhi"}'
    obj_id = add_object(
        name="city info",
        obj_type="JSON",
        content=content,
        tags="location,json",
        description="City data"
    )

    result = tag_object(
        object_id=obj_id,
        tag="India", 
        description="Indian city", 
        schema_hint="geo"
    )
    assert result is True

@pytest.mark.integration
def test_query_by_tag():
    tag_name = "pytest_tag"
    content = b'{"name":  "Charlie"}'
    add_object(
        name="test_tag_obj",
        obj_type="JSON",
        content=content,
        tags=tag_name,
        description="Tagged object"
    )
    result = query_by_tag(tag=tag_name)
    assert isinstance(result, list)
    assert any(b'Charlie' in r for r in result), "Should find the object by tag"

@pytest.mark.integration
def test_query_nonexistent_tag():
    result = query_by_tag("no_such_tag")
    assert isinstance(result, list)
    assert len(result) == 0

if __name__ == "__main__":
    pytest.main(["-v", __file__])