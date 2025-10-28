from src import logger
from src.database import pool
import oracledb

def add_object(name: str, obj_type: str, content: bytes, tags: str,
               description: str = None, schema_hint: str = None):
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            object_id = cursor.callfunc(
                "ora_lake_ops.add_object",
                oracledb.NUMBER,
                [name, obj_type, content, tags, description, schema_hint]
            )
            conn.commit()
            logger.info(f"Object added with ID {object_id}")
            return object_id
    except Exception as e:
        logger.error(f"Error Occurred at add_object: {e}")
        raise


def get_object(object_id: int)->bytes:
    with pool.acquire() as conn:
        cursor = conn.cursor()
        result = cursor.callfunc(
            "ora_lake_ops.get_object",
            bytes,
            [object_id]
        )
        return result


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
