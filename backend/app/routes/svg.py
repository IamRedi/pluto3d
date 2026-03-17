from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import uuid
import requests
from pathlib import Path

from app.services.blueprint_engine import generate_blueprint

router = APIRouter()

UPLOAD_DIR = "uploads"


# ---------------- SVG FROM UPLOADED IMAGE ----------------

@router.post("/svg")
async def create_svg(file: UploadFile = File(...)):

    file_id = str(uuid.uuid4())
    image_path = f"{UPLOAD_DIR}/{file_id}.jpg"

    with open(image_path, "wb") as f:
        f.write(await file.read())

    svg_file = generate_blueprint(image_path)

    # nëse svg_file kthen path si "outputs/xxx.svg"
    filename = Path(svg_file).name

    return {
    "svg_url": f"/outputs/svg/{filename}"
    }


# ---------------- SVG FROM IMAGE URL ----------------

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

    svg_file = generate_blueprint(str(img_path))

    filename = Path(svg_file).name

    return {
    "svg_url": f"/outputs/svg/{filename}"
    }