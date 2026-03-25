import base64
from pathlib import Path

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import get_meshy_api_key

router = APIRouter()

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")


# =========================
# SAVE MODEL
# =========================

def save_model(glb_url, job_id):

    folder = OUTPUT_DIR / job_id
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / "model.glb"
    print("💾 SAVING TO:", file_path)  
    r = requests.get(glb_url, stream=True)

    with open(file_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print("✅ SAVED:", file_path.exists())
    return str(file_path)


# =========================
# REQUEST MODEL
# =========================

class GenerateRequest(BaseModel):
    job_id: str


class GenerateFromImageRequest(BaseModel):
    image_url: str


def _build_meshy_headers(*, include_json_content_type: bool = False) -> dict:
    meshy_api_key = get_meshy_api_key()

    if not meshy_api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "Meshy 3D generation is not configured on this backend. "
                "Set MESHY_API_KEY and restart the server."
            ),
        )

    headers = {
        "Authorization": f"Bearer {meshy_api_key}",
    }

    if include_json_content_type:
        headers["Content-Type"] = "application/json"

    return headers


def _start_meshy_image_to_3d(payload: dict) -> dict:
    try:
        res = requests.post(
            "https://api.meshy.ai/openapi/v1/image-to-3d",
            headers=_build_meshy_headers(include_json_content_type=True),
            json=payload,
            timeout=90,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Meshy request failed before task creation: {exc}",
        ) from exc

    try:
        data = res.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Meshy returned a non-JSON response during task creation.",
        ) from exc

    if res.status_code >= 400:
        raise HTTPException(status_code=502, detail=data)

    task_id = (data.get("result") or "").strip()

    if not task_id:
        raise HTTPException(
            status_code=502,
            detail=data or "Meshy did not return a task id.",
        )

    return {"task_id": task_id}


# =========================
# GENERATE 3D
# =========================

@router.post("/generate")
async def generate_3d(req: GenerateRequest):

    job_id = req.job_id
    job_folder = UPLOAD_DIR / job_id

    if not job_folder.exists():
        return {"error": "Upload folder not found"}

    images = list(job_folder.glob("*"))

    if len(images) == 0:
        return {"error": "No images found"}

    image_path = images[0]

    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    data_uri = f"data:image/png;base64,{img_base64}"

    payload = {
        "image_url": data_uri,
        "enable_pbr": True,
        "should_texture": True
    }

    return _start_meshy_image_to_3d(payload)


@router.post("/image-to-3d")
async def generate_3d_from_upload(req: GenerateRequest):
    return await generate_3d(req)


@router.post("/image-to-3d-pro")
async def generate_3d_pro(req: GenerateFromImageRequest):
    image_url = (req.image_url or "").strip()

    if not image_url:
        raise HTTPException(status_code=400, detail="image_url is required.")

    payload = {
        "image_url": image_url,
        "enable_pbr": True,
        "should_texture": True,
    }

    return _start_meshy_image_to_3d(payload)


# =========================
# CHECK STATUS
# =========================

@router.get("/job/{task_id}")
def check_status(task_id: str):
    try:
        res = requests.get(
            f"https://api.meshy.ai/openapi/v1/image-to-3d/{task_id}",
            headers=_build_meshy_headers(),
            timeout=90,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Meshy status check failed: {exc}",
        ) from exc

    try:
        data = res.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Meshy returned a non-JSON response during status polling.",
        ) from exc

    if res.status_code >= 400:
        raise HTTPException(status_code=502, detail=data)

    print("STATUS RESPONSE:", data)

    status = data.get("status")
    progress = data.get("progress", 0)

    if status == "SUCCEEDED":

        glb_url = data["model_urls"]["glb"]

        save_model(glb_url, task_id)

        return {
    "status": "SUCCEEDED",
    "progress": 100,
    "model_url": f"/outputs/{task_id}/model.glb?ts={task_id}"
}

    return {
        "status": status,
        "progress": progress
    }

@router.post("/generate-free")
async def generate_free(req: GenerateRequest):

    job_id = req.job_id

    job_folder = UPLOAD_DIR / job_id

    if not job_folder.exists():
        return {"error": "No upload"}

    # 🔥 për momentin përdor një model test
    return {
        "status": "DONE",
        "model_url": "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
    }
