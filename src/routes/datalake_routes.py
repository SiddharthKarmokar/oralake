from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import mimetypes
from src.services.ora_lake import add_object

router = APIRouter(prefix="/datalake", tags=["Data Lake"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    tags: str = Form(""),
    description: str = Form(None),
    schema_hint: str = Form(None)
):
    """
    Upload any file to the Oracle Data Lake.
    Extracts metadata and passes to ora_lake.add_object().
    """
    try:
        # --- Extract metadata ---
        name, ext = os.path.splitext(file.filename)
        obj_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

        # --- Read binary content ---
        content = await file.read()

        # --- Call Oracle stored procedure ---
        object_id = add_object(
            name=name,
            obj_type=obj_type,
            content=content,
            tags=tags,
            description=description,
            schema_hint=schema_hint
        )

        # --- Handle response ---
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
