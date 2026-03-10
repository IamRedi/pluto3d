from fastapi import APIRouter
import requests
import base64
from pathlib import Path
from pydantic import BaseModel
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

    r = requests.get(glb_url, stream=True)

    with open(file_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    return str(file_path)


# =========================
# GENERATE 3D
# =========================

class GenerateRequest(BaseModel):
    job_id: str


@router.post("/generate")
async def generate_3d(req: GenerateRequest):

    job_id = req.job_id
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

    data = res.json()

    print("CREATE RESPONSE:", data)

    try:
        task_id = data["result"]["task_id"]
    except:
        return {"error": data}

    return {"task_id": task_id}


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

    print("STATUS RESPONSE:", data)

    # Meshy e kthen status brenda "result"
    result = data.get("result", {})

    status = result.get("status")
    progress = result.get("progress", 0)

    if status == "SUCCEEDED":

        try:
            glb_url = result["model_urls"]["glb"]
        except:
            return {"error": data}

        save_model(glb_url, task_id)

        return {
            "status": "SUCCEEDED",
            "progress": 100,
            "model_url": f"/outputs/{task_id}/model.glb"
        }

    return {
        "status": status,
        "progress": progress
    }