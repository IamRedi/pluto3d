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
from fastapi import APIRouter
from pydantic import BaseModel
import requests
import uuid
from pathlib import Path

router = APIRouter()

class ImageURL(BaseModel):
    image_url: str


@router.post("/svg-from-image")
async def svg_from_image(data: ImageURL):

    img_url = data.image_url

    r = requests.get(img_url)
    filename = f"{uuid.uuid4()}.png"

    img_path = Path("uploads") / filename

    with open(img_path, "wb") as f:
        f.write(r.content)

    # përdor logjikën ekzistuese svg generator
    from app.services.generate_blueprint import generate_blueprint

    svg_file = generate_blueprint(str(img_path))

    return {
        "svg_url": f"/outputs/svg/{svg_file}"
    }