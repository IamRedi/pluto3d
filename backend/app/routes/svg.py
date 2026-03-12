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

    # LOAD IMAGE
    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # SMOOTH
    blur = cv2.GaussianBlur(gray,(5,5),0)

    # THRESHOLD (clean shapes)
    _, thresh = cv2.threshold(blur,120,255,cv2.THRESH_BINARY_INV)

    # MORPH CLOSE (bashkon vijat)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    morph = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel)

    # FIND CONTOURS
    contours,_ = cv2.findContours(
        morph,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    h,w = gray.shape

    with open(output_path,"w") as svg:

        svg.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
        )

        for cnt in contours:

            epsilon = 0.002 * cv2.arcLength(cnt,True)
            approx = cv2.approxPolyDP(cnt,epsilon,True)

            path = "M "

            for p in approx:
                x,y = p[0]
                path += f"{x},{y} "

            path += "Z"

            svg.write(
                f'<path d="{path}" stroke="black" fill="none" stroke-width="1"/>'
            )

        svg.write("</svg>")

    return {
        "svg_url": f"/outputs/svg/{file_id}.svg"
    }