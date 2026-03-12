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

    # READ IMAGE
    img = cv2.imread(input_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # SMOOTH IMAGE
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # EDGE DETECT
    edges = cv2.Canny(blur, 80, 200)

    # FIND CONTOURS
    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    h, w = gray.shape

    # WRITE SVG
    with open(output_path, "w") as svg:

        svg.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        )

        for cnt in contours:

            epsilon = 0.01 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            path = "M "

            for p in approx:
                x, y = p[0]
                path += f"{x},{y} "

            path += "Z"

            svg.write(
                f'<path d="{path}" stroke="black" fill="none" stroke-width="1"/>'
            )

        svg.write("</svg>")

    return {
        "svg_url": f"/outputs/svg/{file_id}.svg"
    }