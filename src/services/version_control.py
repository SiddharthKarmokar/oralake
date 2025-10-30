from src import logger
from src.database import pool
import oracledb

def create_new_version(object_id: int, content: bytes):
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.callproc("ora_lake_version_ops.create_new_version", [object_id, content])
            conn.commit()
            logger.info(f"New version created for object_id={object_id}")
    except Exception as e:
        logger.error(f"Error at create_new_version: {e}")
        raise


def get_version_history(object_id: int):
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            ref_cursor = cursor.callfunc(
                "ora_lake_version_ops.get_version_history",
                oracledb.CURSOR,
                [object_id]
            )
            versions = ref_cursor.fetchall()
            logger.info(f"Fetched {len(versions)} versions for object_id={object_id}")
            return versions
    except Exception as e:
        logger.error(f"Error at get_version_history: {e}")
        raise


def restore_version(object_id: int, version_number: int):
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.callproc("ora_lake_version_ops.restore_version", [object_id, version_number])
            conn.commit()
            logger.info(f"Restored object_id={object_id} to version {version_number}")
    except Exception as e:
        logger.error(f"Error at restore_version: {e}")
        raise
