from src import logger
from src.database import pool


def add_object(name: str, obj_type: str, content: bytes, tags: str, description: str = None, schema_hint: str = None):
    with pool.acquire() as conn:
        cursor = conn.cursor()
        cursor.callproc(
            "ora_lake_ops.add_object",
            [name, obj_type, content, tags, description, schema_hint]
        )
        conn.commit()


