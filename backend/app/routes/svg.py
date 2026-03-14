from fastapi import APIRouter, UploadFile, File
import uuid
import os

from app.services.blueprint_engine import generate_blueprint

router = APIRouter()

UPLOAD_DIR = "uploads"


@router.post("/svg")
async def create_svg(file: UploadFile = File(...)):

    file_id = str(uuid.uuid4())

    image_path = f"{UPLOAD_DIR}/{file_id}.jpg"

    with open(image_path, "wb") as f:
        f.write(await file.read())

    svg_path = generate_blueprint(image_path)

    return {
        "svg_url": "/" + svg_path
    }