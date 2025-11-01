from src import logger
from src.database import pool
from typing import List, Optional
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
            
            # Use oracledb.BLOB for proper BLOB handling
            result = cursor.var(oracledb.BLOB)
            cursor.execute(
                "BEGIN :result := ora_lake_ops.get_object(:id); END;",
                result=result,
                id=object_id
            )
            
            # Read the BLOB data
            if result.getvalue() is not None:
                blob_data = result.getvalue().read()
                logger.info(f"Object found: {len(blob_data)} bytes")
                return blob_data
            else:
                logger.warning(f"Object with ID: {object_id} was not found")
                return None
                
    except oracledb.DatabaseError as e:
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

def tag_object(object_id: int, tag: str, description: str = None, schema_hint: str = None)->bool:
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.callproc(
                "ora_lake_ops.tag_object",
                [object_id, tag, description, schema_hint]
            )
            conn.commit()
            logger.info(f"Object with object_id {object_id} was tagged")
            return True
    except oracledb.DatabaseError as e:
        error_obj = e.args[0]
        error_msg = str(error_obj)

        if "PLS-00302" in error_msg:
            logger.error("Procedure 'tag_objects' does not exist in ORA_LAKE_OPS package.")
            return False

        if "ORA-02291" in error_msg:
            logger.warning(f"Object with ID: {object_id} was not found")
            return False

        logger.error(f"Database Error occurred at get_object: {e}")
        raise
    except Exception as e:
        logger.error(f"Error occured at get_object: {e}")
        raise

def query_by_tag(tag: str)->List[bytes]:
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()

            ref_cursor = cursor.callfunc(
                "ora_lake_ops.query_objects_by_tag",
                oracledb.CURSOR,
                [tag]
            )
            results = ref_cursor.fetchall()
            objects = []
            for res in results:
                object_id = res[0]
                obj_content = get_object(object_id=object_id)
                if obj_content:
                    objects.append(obj_content)
            logger.info(f"Fetched {len(results)} objects for tag='{tag}'")
            return objects
    except oracledb.DatabaseError as e:
        error_obj = e.args[0]
        error_msg = str(error_obj)

        if "PLS-00302" in error_msg:
            logger.error("Procedure 'query_object_by_tag' does not exist in ORA_LAKE_OPS package.")
            return False

        if "ORA-02291" in error_msg:
            logger.warning(f"Object with ID: {object_id} was not found")
            return False

        logger.error(f"Database Error occurred at get_object: {e}")
        raise
    except Exception as e:
        logger.error(f"Error occured at get_object: {e}")
        raise

def update_object(name: str, obj_type: str, content: bytes, tags: str,
                  description: Optional[str] = None) -> bool:
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.callproc(
                "ora_lake_ops.update_object",
                [name, obj_type, content, tags, description]
            )
            conn.commit()
            logger.info(f"Object '{name}' updated successfully.")
            return True
    except Exception as e:
        logger.error(f"Error occurred at update_object: {e}")
        raise


def rollback_object(name: str, obj_type: str, version: int) -> bool:
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.callproc(
                "ora_lake_ops.rollback_object",
                [name, obj_type, version]
            )
            conn.commit()
            logger.info(f"Rolled back '{name}' ({obj_type}) to version {version}.")
            return True
    except Exception as e:
        logger.error(f"Error occurred at rollback_object: {e}")
        raise


if __name__ == "__main__":
    result = query_by_tag(
        tag = "csv"
    )
    logger.info(result)