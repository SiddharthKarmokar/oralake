from fastapi import APIRouter
from src.database import connect_oracledb
from oracledb.exceptions import DatabaseError

router = APIRouter(prefix="/oracle", tags=["Oracle"])

@router.get("/test")
async def test_connection():
    """
    Simple endpoint to test Oracle connection.
    """
    try:
        with connect_oracledb() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 'Connected to Oracle!' FROM dual")
                msg = cur.fetchone()[0]
                return {"message": msg}
    except DatabaseError as e:
        return {"error": f"Database error: {e}"}
    except Exception as e:
        return {"error": str(e)}
