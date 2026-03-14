from ultralytics import YOLO

# load model
model = YOLO("yolov8n.pt")

# klasat që na interesojnë
VEHICLE_CLASSES = ["car", "truck", "bus", "motorcycle"]


def detect_main_object(image, confidence=0.80):

    results = model(image)

    best_box = None
    best_conf = 0

    for r in results:

        for box in r.boxes:

            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            conf = float(box.conf[0])

            if label not in VEHICLE_CLASSES:
                continue

            if conf >= confidence and conf > best_conf:

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                best_box = (x1, y1, x2, y2)
                best_conf = conf

    return best_box