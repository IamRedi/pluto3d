import cv2
import svgwrite
import uuid
import os
import numpy as np


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "../../outputs/svg")
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def prepare_edges(gray, detail_level="normal"):
    level = (detail_level or "normal").lower()

    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)

    if level == "less":
        processed = cv2.GaussianBlur(bilateral, (7, 7), 0)
        low, high = 48, 128
    elif level == "more":
        soft = cv2.GaussianBlur(bilateral, (3, 3), 0)
        processed = cv2.addWeighted(bilateral, 1.18, soft, -0.18, 0)
        low, high = 36, 112
    else:
        processed = cv2.GaussianBlur(bilateral, (5, 5), 0)
        low, high = 40, 120

    return cv2.Canny(processed, low, high)


def clean_background(img, level="soft"):
    level = (level or "soft").lower()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    _, mask = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    kernel_size = 5 if level == "soft" else 7
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img

    largest = max(contours, key=cv2.contourArea)
    minimum_ratio = 0.04 if level == "soft" else 0.025
    if cv2.contourArea(largest) < (img.shape[0] * img.shape[1]) * minimum_ratio:
        return img

    clean_mask = np.zeros_like(mask)
    cv2.drawContours(clean_mask, [largest], -1, 255, thickness=cv2.FILLED)
    blur_size = 7 if level == "soft" else 11
    clean_mask = cv2.GaussianBlur(clean_mask, (blur_size, blur_size), 0)

    foreground = cv2.bitwise_and(img, img, mask=clean_mask)
    white_bg = np.full_like(img, 255)
    inverse_mask = cv2.bitwise_not(clean_mask)
    background = cv2.bitwise_and(white_bg, white_bg, mask=inverse_mask)

    return cv2.add(foreground, background)


def generate_blueprint(
    image_path,
    detail_level="normal",
    clean_background_level="off",
):
    print("Saving SVG to:", OUTPUT_DIR)

    img = cv2.imread(image_path)

    if img is None:
        raise Exception(f"Image not found: {image_path}")

    print("Using full image for SVG subject framing")

    if clean_background_level and clean_background_level != "off":
        img = clean_background(img, level=clean_background_level)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = prepare_edges(gray, detail_level=detail_level)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE,
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
                stroke="black",
                fill="none",
                stroke_width=1,
            )
        )

    dwg.save()

    return output
