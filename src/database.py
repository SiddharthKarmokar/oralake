import oracledb
from oracledb.exceptions import DatabaseError
from src.secrets import secrets
from src import logger

oracledb.init_oracle_client(lib_dir=None)

pool = oracledb.create_pool(
    user = secrets.ORACLE_USER,
    password = secrets.ORACLE_PASSWORD,
    dsn = secrets.ORACLE_DSN,
    min=2,
    max=5,
    increment=1
)


def connect_oracledb()->oracledb.Connection:
    return pool.acquire()


if __name__ == "__main__":
    try:
        with connect_oracledb() as conn:
            cursor = conn.cursor
            cursor.execute("SELECT 'Connected to OracleDB!' from dual")
            message = cursor.fetchone()[0]
            print(message)
    except DatabaseError as e:
        logger.exception("No Listener available")
        raise e
    except Exception as e:
        logger.error(f"Error at database.py: {e}")