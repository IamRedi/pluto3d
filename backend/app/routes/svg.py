from fastapi import APIRouter, UploadFile, File, Form
import uuid
import os
import cv2
import numpy as np

router = APIRouter()

UPLOAD_DIR = "uploads"
SVG_DIR = "outputs/svg"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SVG_DIR, exist_ok=True)


def contours_to_svg(contours, w, h, output_path):

    with open(output_path, "w") as svg:

        svg.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">')

        for cnt in contours:

            if cv2.contourArea(cnt) < 80:
                continue

            epsilon = 0.002 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            path = "M "

            for p in approx:
                x, y = p[0]
                path += f"{x},{y} "

            svg.write(
                f'<path d="{path}" stroke="black" fill="none" stroke-width="1"/>'
            )

        svg.write("</svg>")


@router.post("/svg")
async def generate_svg(
    file: UploadFile = File(...),
    mode: str = Form("outline")
):

    file_id = str(uuid.uuid4())

    input_path = f"{UPLOAD_DIR}/{file_id}.png"
    output_path = f"{SVG_DIR}/{file_id}.svg"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape

    if mode == "outline":

        blur = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(blur, 80, 200)

        contours,_ = cv2.findContours(
            edges,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE
        )


    elif mode == "engrave":

        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11,
            2
        )

        kernel = np.ones((3,3),np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours,_ = cv2.findContours(
            morph,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE
        )


    elif mode == "stencil":

        _,thresh = cv2.threshold(
            gray,
            120,
            255,
            cv2.THRESH_BINARY_INV
        )

        kernel = np.ones((5,5),np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours,_ = cv2.findContours(
            morph,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )


    contours_to_svg(contours, w, h, output_path)

    return {
        "svg_url": f"/outputs/svg/{file_id}.svg"
    }