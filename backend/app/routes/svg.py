from fastapi import APIRouter, UploadFile, File
import uuid
import os
import vtracer

router = APIRouter()

UPLOAD_DIR = "uploads"
SVG_DIR = "outputs/svg"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SVG_DIR, exist_ok=True)


@router.post("/svg")
async def generate_svg(file: UploadFile = File(...)):

    file_id = str(uuid.uuid4())

    input_path = f"{UPLOAD_DIR}/{file_id}.png"
    output_path = f"{SVG_DIR}/{file_id}.svg"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    vtracer.convert_image_to_svg(
        input_path,
        output_path
    )

    return {
        "svg_url": f"/outputs/svg/{file_id}.svg"
    }