from fastapi import APIRouter, UploadFile, File, Form
from app.config import UPLOAD_DIR

router = APIRouter()

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    job_id: str = Form(...)
):

    job_folder = UPLOAD_DIR / job_id
    job_folder.mkdir(parents=True, exist_ok=True)

    file_path = job_folder / file.filename

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {
        "job_id": job_id,
        "filename": file.filename
    }