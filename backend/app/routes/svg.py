from fastapi import APIRouter, UploadFile, File, Form
import uuid
import os
import cv2
import subprocess

router = APIRouter()

UPLOAD_DIR = "uploads"
SVG_DIR = "outputs/svg"
TMP_DIR = "tmp"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SVG_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)


@router.post("/svg")
async def generate_svg(
    file: UploadFile = File(...),
    mode: str = Form("outline")
):

    file_id = str(uuid.uuid4())

    input_path = f"{UPLOAD_DIR}/{file_id}.png"
    bitmap_path = f"{TMP_DIR}/{file_id}.pbm"
    output_svg = f"{SVG_DIR}/{file_id}.svg"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ---------- MODE SELECTION ----------

    if mode == "outline":

        blur = cv2.GaussianBlur(gray,(5,5),0)
        edges = cv2.Canny(blur,80,200)

        processed = edges

    elif mode == "engrave":

        processed = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11,
            2
        )

    elif mode == "stencil":

        _,processed = cv2.threshold(
            gray,
            120,
            255,
            cv2.THRESH_BINARY_INV
        )

        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,(5,5)
        )

        processed = cv2.morphologyEx(
            processed,
            cv2.MORPH_CLOSE,
            kernel
        )

    else:

        processed = gray

    # ---------- SAVE BITMAP ----------

    cv2.imwrite(bitmap_path, processed)

    # ---------- POTRACE ----------

    subprocess.run([
    "/usr/bin/potrace",
        bitmap_path,
        "-s",
        "-o",
        output_svg,
        "--turdsize","10",
        "--alphamax","1",
        "--opttolerance","0.2"
    ])

    return {
        "svg_url": f"/outputs/svg/{file_id}.svg"
    }
