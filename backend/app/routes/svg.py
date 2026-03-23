from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
import uuid
import requests
from pathlib import Path
from typing import Literal

from app.services.blueprint_engine import generate_blueprint

router = APIRouter()

UPLOAD_DIR = "uploads"

SVGDetail = Literal["less", "normal", "more"]
SVGBackground = Literal["off", "soft", "strong"]


# ---------------- SVG FROM UPLOADED IMAGE ----------------

@router.post("/svg")
async def create_svg(
    file: UploadFile = File(...),
    detail: SVGDetail = Form("normal"),
    clean_background: SVGBackground = Form("off"),
):

    file_id = str(uuid.uuid4())
    image_path = f"{UPLOAD_DIR}/{file_id}.jpg"

    with open(image_path, "wb") as f:
        f.write(await file.read())

    svg_file = generate_blueprint(
        image_path,
        detail_level=detail,
        clean_background_level=clean_background,
    )

    # nëse svg_file kthen path si "outputs/xxx.svg"
    filename = Path(svg_file).name

    return {
    "svg_url": f"/outputs/svg/{filename}",
    "detail": detail,
    "clean_background": clean_background
    }


# ---------------- SVG FROM IMAGE URL ----------------

class ImageURL(BaseModel):
    image_url: str
    detail: SVGDetail = "normal"
    clean_background: SVGBackground = "off"


@router.post("/svg-from-image")
async def svg_from_image(data: ImageURL):

    img_url = data.image_url

    r = requests.get(img_url)

    filename = f"{uuid.uuid4()}.png"
    img_path = Path("uploads") / filename

    with open(img_path, "wb") as f:
        f.write(r.content)

    svg_file = generate_blueprint(
        str(img_path),
        detail_level=data.detail,
        clean_background_level=data.clean_background,
    )

    filename = Path(svg_file).name

    return {
    "svg_url": f"/outputs/svg/{filename}",
    "detail": data.detail,
    "clean_background": data.clean_background
    }


from fastapi import UploadFile, File
from rembg import remove
import uuid
import os

@router.post("/silhouette")
async def silhouette(file: UploadFile = File(...)):

    contents = await file.read()

    # TEMP disable rembg for Railway
    output = contents

    filename = f"silhouette_{uuid.uuid4()}.png"
    path = f"outputs/{filename}"

    with open(path, "wb") as f:
        f.write(output)

    return {
        "image_url": f"/outputs/{filename}"
    }
