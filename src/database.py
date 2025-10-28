import oracledb
from src.secrets import secrets
from src import logger

# DSN format: host:port/service_name
DSN = secrets.ORACLE_DSN 

pool = oracledb.create_pool(
    user=secrets.ORACLE_USER,
    password=secrets.ORACLE_PASSWORD,
    dsn=DSN,
    min=2,
    max=5,
    increment=1,
    mode=oracledb.DEFAULT_AUTH,
)

def connect_oracledb() -> oracledb.Connection:
    """Acquire a connection from the pool."""
    return pool.acquire()

if __name__ == "__main__":
    try:
        with connect_oracledb() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 'Connected to OracleDB!' FROM dual")
            message = cursor.fetchone()[0]
            print(message)
    except oracledb.DatabaseError as e:
        logger.exception("Database error occurred")
        raise e
    except Exception as e:
        logger.error(f"Error in database.py: {e}")
