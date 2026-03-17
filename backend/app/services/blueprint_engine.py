import cv2
import svgwrite
import uuid
import os

from app.services.crop_object import crop_object

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "../../outputs/svg")
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_blueprint(image_path):

    print("Saving SVG to:", OUTPUT_DIR)

    img = cv2.imread(image_path)

    if img is None:
        raise Exception(f"Image not found: {image_path}")

    # ---------------- OBJECT DETECTION ----------------

    boxes = []

    if len(boxes) > 0:
        box = boxes[0]
        print("Object detected → cropping")
        img = crop_object(img, box)
    else:
        print("No object detected → using full image")

    # ---------------- EDGE PREPROCESS ----------------

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 40, 120)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE
    )

    h, w = edges.shape[:2]

    name = f"{uuid.uuid4()}.svg"
    output = os.path.join(OUTPUT_DIR, name)

    dwg = svgwrite.Drawing(output, size=(w, h))

    for cnt in contours:

        if cv2.contourArea(cnt) < 5:
            continue

        epsilon = 0.002 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        points = [(int(p[0][0]), int(p[0][1])) for p in approx]

        if len(points) < 2:
            continue

        dwg.add(
            dwg.polyline(
                points,
                stroke="white",
                fill="none",
                stroke_width=1
            )
        )

    dwg.save()

    return output