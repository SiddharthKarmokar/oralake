from src.services.ora_lake import add_object

if __name__ == "__main__":
    content = b'{"name": "Alice", "age":25}'
    add_object(
        name="user_1",
        obj_type="JSON",
        content=content,
        tags="demo,json",
        description="Test JSON file"
    )