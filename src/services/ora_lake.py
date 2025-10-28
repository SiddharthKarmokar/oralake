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
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            result = cursor.callfunc(
                "ora_lake_ops.get_object",
                bytes,
                [object_id]
            )
            logger.info(f"Object found: {result}")
            return result
    except oracledb.exceptions.DatabaseError as e:
        error_obj = e.args[0]
        error_msg = str(error_obj)

        if "ORA-01403" in error_msg:
            logger.warning(f"Object with ID: {object_id} was not found")
            return None

        logger.error(f"Database Error occurred at get_object: {e}")
        raise
    except Exception as e:
        logger.error(f"Error occured at get_object: {e}")
        raise

if __name__ == "__main__":
    result = get_object(
        object_id=9
    )
    logger.info(result)
