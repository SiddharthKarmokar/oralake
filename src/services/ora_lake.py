from src import logger
from src.database import pool


def add_object(name: str, obj_type: str, content: bytes, tags: str, description: str = None, schema_hint: str = None)->bool:
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.callproc(
                "ora_lake_ops.add_object",
                [name, obj_type, content, tags, description, schema_hint]
            )
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error Occurred at add_object", e)
        return False

if __name__ == "__main__":
    file_content = b"Hello, this is a test object content."

    add_object(
        name="sample_doc.txt",
        obj_type="TEXT",
        content=file_content,
        tags="demo,test",
        description="A simple sample text object",
        schema_hint=None
    )
