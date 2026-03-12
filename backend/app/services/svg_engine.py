import cv2
import numpy as np


# -----------------------------
# Resize për stabilitet
# -----------------------------

def resize_image(img, max_size=1400):

    h, w = img.shape[:2]

    scale = max_size / max(h, w)

    if scale < 1:
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    return img


# -----------------------------
# Preprocess profesional
# -----------------------------

def preprocess(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ruan edges por pastron zhurmën
    blur = cv2.bilateralFilter(gray, 9, 80, 80)

    # contrast boost
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
    contrast = clahe.apply(blur)

    return contrast


# -----------------------------
# Edge detection sipas mode
# -----------------------------

def detect_edges(img, mode):

    if mode == "outline":

        edges = cv2.Canny(img, 70, 170)

    elif mode == "engrave":

        edges = cv2.adaptiveThreshold(
            img,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            15,
            3
        )

    elif mode == "stencil":

        _, edges = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY_INV)

        kernel = np.ones((4,4), np.uint8)

        edges = cv2.dilate(edges, kernel, iterations=2)

    else:

        edges = cv2.Canny(img, 70, 170)

    return edges


# -----------------------------
# Noise cleanup
# -----------------------------

def clean_edges(edges):

    kernel = np.ones((2,2),np.uint8)

    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    edges = cv2.medianBlur(edges,3)

    return edges


# -----------------------------
# Contour simplification
# -----------------------------

def simplify_contour(cnt):

    epsilon = 0.002 * cv2.arcLength(cnt, True)

    approx = cv2.approxPolyDP(cnt, epsilon, True)

    return approx


# -----------------------------
# Curve smoothing
# -----------------------------

def smooth_contour(cnt):

    if len(cnt) < 5:
        return cnt

    cnt = cnt.reshape(-1,2)

    x = cnt[:,0]
    y = cnt[:,1]

    x = cv2.GaussianBlur(x.astype(np.float32),(5,1),0)
    y = cv2.GaussianBlur(y.astype(np.float32),(5,1),0)

    smooth = np.stack((x,y),axis=1)

    smooth = smooth.astype(np.int32).reshape(-1,1,2)

    return smooth


# -----------------------------
# Contours → SVG
# -----------------------------

def contours_to_svg(contours, width, height):

    svg = []

    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">')

    svg.append('<g fill="none" stroke="black" stroke-width="1">')

    for cnt in contours:

        if cv2.contourArea(cnt) < 30:
            continue

        path = "M "

        for p in cnt:

            x, y = p[0]

            path += f"{x},{y} "

        svg.append(f'<path d="{path}" />')

    svg.append("</g>")
    svg.append("</svg>")

    return "\n".join(svg)


# -----------------------------
# MAIN ENGINE
# -----------------------------

def generate_svg(image_path, mode):

    img = cv2.imread(image_path)

    img = resize_image(img)

    h, w = img.shape[:2]

    processed = preprocess(img)

    edges = detect_edges(processed, mode)

    edges = clean_edges(edges)

    contours,_ = cv2.findContours(
        edges,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_NONE
    )

    processed_contours = []

    for c in contours:

        if cv2.contourArea(c) < 20:
            continue

        c = simplify_contour(c)

        c = smooth_contour(c)

        processed_contours.append(c)

    svg = contours_to_svg(processed_contours, w, h)

    return svg