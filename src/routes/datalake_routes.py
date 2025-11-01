# from fastapi import APIRouter, UploadFile, File, Form, HTTPException
# import os
# import mimetypes
# import base64
# from src.services.oralake import add_object, get_object
# from src.services.oralake import query_by_tag

# router = APIRouter(prefix="/datalake", tags=["Data Lake"])

# # ------------------------------
# # 1️⃣ Upload Object
# # ------------------------------
# @router.post("/upload")
# async def upload_file(
#     file: UploadFile = File(...),
#     tags: str = Form(""),
#     description: str = Form(None),
#     schema_hint: str = Form(None)
# ):
#     try:
#         name, ext = os.path.splitext(file.filename)
#         obj_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
#         content = await file.read()

#         object_id = add_object(
#             name=name,
#             obj_type=obj_type,
#             content=content,
#             tags=tags,
#             description=description,
#             schema_hint=schema_hint
#         )

#         if isinstance(object_id, int) and object_id > -1:
#             return {
#                 "status": "success",
#                 "object_id": object_id,
#                 "filename": file.filename,
#                 "type": obj_type,
#                 "size_kb": round(len(content) / 1024, 2)
#             }
#         else:
#             return {"status": "failure", "message": "Failed to add object."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ------------------------------
# # 2️⃣ Get Object by ID
# # ------------------------------
# @router.get("/get/{object_id}")
# def get_object_by_id(object_id: int):
#     try:
#         content = get_object(object_id)
#         if not content:
#             raise HTTPException(status_code=404, detail="Object not found")

#         encoded_content = base64.b64encode(content).decode("utf-8")
#         return {
#             "object_id": object_id,
#             "filename": f"object_{object_id}.bin",
#             "type": "application/octet-stream",
#             "content": encoded_content
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ------------------------------
# # 3 Query by Tag
# # ------------------------------

# @router.get("/query-by-tag/{tag}")
# async def query_objects(tag: str):
#     """
#     Fetch all objects having the given tag.
#     """
#     try:
#         results = query_by_tag(tag)
#         if results and isinstance(results, list) and len(results) > 0:
#             return {"status": "success", "count": len(results), "objects": results}
#         else:
#             return {"status": "empty", "message": f"No objects found for tag '{tag}'."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import mimetypes
import base64
from datetime import datetime
from src.services.oralake import add_object, get_object, query_by_tag

router = APIRouter(prefix="/datalake", tags=["Data Lake"])

# ------------------------------
# 1️⃣ Upload Object (with Version & Timestamp)
# ------------------------------
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    tags: str = Form(""),
    description: str = Form(None),
    schema_hint: str = Form(None)
):
    """
    Upload a file to the Oracle Data Lake.
    The backend handles versioning and timestamp generation.
    """
    try:
        name, ext = os.path.splitext(file.filename)
        obj_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        content = await file.read()

        # Backend returns dict including version & timestamp
        result = add_object(
            name=name,
            obj_type=obj_type,
            content=content,
            tags=tags,
            description=description,
            schema_hint=schema_hint
        )

        # Handle both dict and int (backward compatible)
        if isinstance(result, dict) and result.get("status") == "success":
            return {
                "status": "success",
                "object_id": result.get("object_id"),
                "filename": file.filename,
                "type": obj_type,
                "size_kb": round(len(content) / 1024, 2),
                "version": result.get("version"),
                "timestamp": result.get("timestamp"),
            }

        elif isinstance(result, int) and result > -1:
            # Fallback for legacy backend
            return {
                "status": "success",
                "object_id": result,
                "filename": file.filename,
                "type": obj_type,
                "size_kb": round(len(content) / 1024, 2),
                "version": None,
                "timestamp": datetime.now().isoformat(),
            }

        else:
            return {"status": "failure", "message": "Failed to add object."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------
# 2️⃣ Get Object by ID (used internally)
# ------------------------------
@router.get("/get/{object_id}")
def get_object_by_id(object_id: int):
    """
    Retrieve an object by its ID and return Base64 encoded content.
    """
    try:
        content = get_object(object_id)
        if not content:
            raise HTTPException(status_code=404, detail="Object not found")

        encoded_content = base64.b64encode(content).decode("utf-8")
        return {
            "status": "success",
            "object_id": object_id,
            "filename": f"object_{object_id}.bin",
            "type": "application/octet-stream",
            "content": encoded_content,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------
# 3️⃣ Query by Tag
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


# ------------------------------
# 4️⃣ View Object (For Streamlit Viewer)
# ------------------------------
@router.get("/view/{object_id}")
def view_object(object_id: int):
    """
    Fetch object details for the viewer — includes Base64 content, type, version, timestamp.
    """
    try:
        data = get_object(object_id)
        if not data:
            raise HTTPException(status_code=404, detail="Object not found")

        encoded_content = base64.b64encode(data).decode("utf-8")

        return {
            "status": "success",
            "object_id": object_id,
            "filename": f"object_{object_id}.bin",
            "type": "application/octet-stream",
            "version": "v1.0",  # optional – replace with real version if stored
            "timestamp": datetime.now().isoformat(),  # optional – replace if stored in DB
            "content": encoded_content,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
