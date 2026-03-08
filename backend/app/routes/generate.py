from fastapi import APIRouter
import requests
import base64
import os
from app.config import UPLOAD_DIR, MESHY_API_KEY

router = APIRouter()


# =========================
# SAVE MODEL
# =========================
def save_model(glb_url, job_id):

    folder = f"outputs/{job_id}"
    os.makedirs(folder, exist_ok=True)

    file_path = f"{folder}/model.glb"

    r = requests.get(glb_url)

    with open(file_path, "wb") as f:
        f.write(r.content)

    return file_path


# =========================
# CREATE AI TASK
# =========================
@router.post("/generate")
async def generate_3d(job_id: str):

    job_folder = UPLOAD_DIR / job_id
    images = list(job_folder.glob("*"))

    if len(images) == 0:
        return {"error": "No images"}

    image_path = images[0]

    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    data_uri = f"data:image/png;base64,{img_base64}"

    headers = {
        "Authorization": f"Bearer {MESHY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "image_url": data_uri,
        "enable_pbr": True,
        "should_texture": True
    }

    res = requests.post(
        "https://api.meshy.ai/openapi/v1/image-to-3d",
        headers=headers,
        json=payload
    )

    task = res.json()

    return {
        "task_id": task["result"]
    }


# =========================
# CHECK TASK STATUS
# =========================
@router.get("/job/{task_id}")
def check_status(task_id: str):

    headers = {
        "Authorization": f"Bearer {MESHY_API_KEY}"
    }

    res = requests.get(
        f"https://api.meshy.ai/openapi/v1/image-to-3d/{task_id}",
        headers=headers
    )

    data = res.json()

    status = data.get("status")

    if status == "SUCCEEDED" and "result" in data:

        glb_url = data["result"]["model_urls"]["glb"]

        save_model(glb_url, task_id)

        return {
            "status": "SUCCEEDED",
            "model_url": f"/outputs/{task_id}/model.glb"
        }

    return data
from pathlib import Path

@router.get("/models")
def list_models():

    base = Path("outputs")

    models = []

    if base.exists():

        for folder in base.iterdir():

            model = folder / "model.glb"

            if model.exists():

                models.append(f"/outputs/{folder.name}/model.glb")

    return {"models": models}

import os
import base64

@router.post("/preview")
def save_preview(data: dict):

    job_id = data["job_id"]
    image = data["image"]

    # remove base64 header
    image = image.split(",")[1]

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    outputs_dir = os.path.join(base_dir, "outputs")

    job_folder = os.path.join(outputs_dir, job_id)

    # create folder if not exists
    os.makedirs(job_folder, exist_ok=True)

    preview_path = os.path.join(job_folder, "preview.png")

    with open(preview_path, "wb") as f:
        f.write(base64.b64decode(image))

    return {"status": "preview_saved"}