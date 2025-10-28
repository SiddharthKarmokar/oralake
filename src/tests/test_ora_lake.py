from src.services.ora_lake import add_object
import pytest

@pytest.mark.integration
def test_add_object(monkeypatch):
    content = b'{"name": "Alice", "age":25}'
    called = {}
    def mock_add_object(name: str, obj_type: str, content: bytes, tags: str, description: str = None, schema_hint: str = None):
        called.update({
            "name": name,
            "obj_type": obj_type, 
            "content": content, 
            "tags": tags, 
            "description": description, 
            "schema_hint": schema_hint
        })
        return 1
    
    monkeypatch.setattr("src.services.ora_lake", mock_add_object)
    res = add_object(
        name="user_1",
        obj_type="JSON",
        content=content,
        tags="demo,json",
        description="Test JSON file"
    )

    assert res is int
    assert called["name"] == "user_1"
    assert called["obj_type"] == "JSON"
    assert called["tags"] == "demo,json"
    assert b"Alice" in called["content"]



if __name__ == "__main__":
    content = b'{"name": "Alice", "age":25}'
    add_object(
        name="user_1",
        obj_type="JSON",
        content=content,
        tags="demo,json",
        description="Test JSON file"
    )