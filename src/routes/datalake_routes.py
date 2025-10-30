from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import mimetypes
import base64
from src.services.ora_lake import add_object, get_object
from src.services.ora_lake import query_by_tag

router = APIRouter(prefix="/datalake", tags=["Data Lake"])

# ------------------------------
# 1️⃣ Upload Object
# ------------------------------
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    tags: str = Form(""),
    description: str = Form(None),
    schema_hint: str = Form(None)
):
    try:
        name, ext = os.path.splitext(file.filename)
        obj_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        content = await file.read()

        object_id = add_object(
            name=name,
            obj_type=obj_type,
            content=content,
            tags=tags,
            description=description,
            schema_hint=schema_hint
        )

        if isinstance(object_id, int) and object_id > -1:
            return {
                "status": "success",
                "object_id": object_id,
                "filename": file.filename,
                "type": obj_type,
                "size_kb": round(len(content) / 1024, 2)
            }
        else:
            return {"status": "failure", "message": "Failed to add object."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------
# 2️⃣ Get Object by ID
# ------------------------------
@router.get("/get/{object_id}")
def get_object_by_id(object_id: int):
    try:
        content = get_object(object_id)
        if not content:
            raise HTTPException(status_code=404, detail="Object not found")

        encoded_content = base64.b64encode(content).decode("utf-8")
        return {
            "object_id": object_id,
            "filename": f"object_{object_id}.bin",
            "type": "application/octet-stream",
            "content": encoded_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------
# 3 Query by Tag
# ------------------------------

@router.get("/query-by-tag/{tag}")
async def query_objects(tag: str):
    """
    Fetch all objects having the given tag.
    """
    try:
        results = query_by_tag(tag)
        if results and isinstance(results, list) and len(results) > 0:
            return {"status": "success", "count": len(results), "objects": results}
        else:
            return {"status": "empty", "message": f"No objects found for tag '{tag}'."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

