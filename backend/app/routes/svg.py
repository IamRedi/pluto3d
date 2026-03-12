from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
import uuid

from app.services.svg_engine import generate_svg

router = APIRouter()

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs/svg")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/svg")
async def create_svg(
    file: UploadFile = File(...),
    mode: str = Form(...)
):

    uid = str(uuid.uuid4())

    input_path = UPLOAD_DIR / f"{uid}.png"

    with open(input_path,"wb") as f:
        f.write(await file.read())

    svg_content = generate_svg(str(input_path), mode)

    svg_path = OUTPUT_DIR / f"{uid}.svg"

    with open(svg_path,"w") as f:
        f.write(svg_content)

    return {
        "svg_url": f"/outputs/svg/{uid}.svg"
    }