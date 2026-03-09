from fastapi import APIRouter, UploadFile, File
import uuid
import os
import cv2

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

    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(img,100,200)

    h, w = edges.shape

    with open(output_path, "w") as svg:
        svg.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">')
        for y in range(h):
            for x in range(w):
                if edges[y][x] > 0:
                    svg.write(f'<rect x="{x}" y="{y}" width="1" height="1" fill="black"/>')
        svg.write('</svg>')

    return {
        "svg_url": f"/outputs/svg/{file_id}.svg"
    }