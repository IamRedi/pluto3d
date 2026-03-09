from fastapi import APIRouter
import requests
import base64
from pathlib import Path
from app.config import MESHY_API_KEY

router = APIRouter()

UPLOAD_DIR = Path("uploads")


# =========================
# SAVE MODEL
# =========================

def save_model(glb_url, job_id):

    folder = Path("outputs") / job_id
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / "model.glb"

    r = requests.get(glb_url)

    with open(file_path, "wb") as f:
        f.write(r.content)

    return str(file_path)


# =========================
# GENERATE 3D
# =========================

@router.post("/generate")
async def generate_3d(job_id: str):

    job_folder = UPLOAD_DIR / job_id

    images = list(job_folder.glob("*"))

    if len(images) == 0:
        return {"error": "No images found"}

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

    if "result" not in task:
        return {"error": task}

    return {"task_id": task["result"]}


# =========================
# CHECK STATUS
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

    if status == "SUCCEEDED":

        glb_url = data["result"]["model_urls"]["glb"]

        save_model(glb_url, task_id)

        return {
            "status": "SUCCEEDED",
            "model_url": f"/outputs/{task_id}/model.glb"
        }

    return data