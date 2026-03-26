import base64
from pathlib import Path

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import get_meshy_api_key

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
TERMINAL_FAILURE_STATUSES = {"FAILED", "CANCELED", "CANCELLED", "EXPIRED", "ERROR"}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_model(glb_url: str, job_id: str) -> str:
    if not glb_url:
        raise HTTPException(
            status_code=502,
            detail="Meshy completed the task without a GLB download URL.",
        )

    folder = OUTPUT_DIR / job_id
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / "model.glb"

    try:
        with requests.get(glb_url, stream=True, timeout=90) as response:
            response.raise_for_status()
            with open(file_path, "wb") as file_handle:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file_handle.write(chunk)
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to download the Meshy GLB output: {exc}",
        ) from exc

    return str(file_path)


class GenerateRequest(BaseModel):
    job_id: str


class GenerateFromImageRequest(BaseModel):
    image_url: str


def _extract_meshy_task_id(data: dict) -> str:
    return (data.get("result") or data.get("task_id") or "").strip()


def _extract_progress_value(raw_progress) -> int:
    if raw_progress in (None, ""):
        return 0

    try:
        progress = float(raw_progress)
    except (TypeError, ValueError):
        return 0

    if progress <= 1:
        progress *= 100

    return max(0, min(100, int(round(progress))))


def _extract_failure_message(data: dict) -> str:
    for key in ("message", "detail", "error", "error_message"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return "Meshy could not complete the 3D generation task."


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
        response = requests.post(
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
        data = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Meshy returned a non-JSON response during task creation.",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=data)

    task_id = _extract_meshy_task_id(data)

    if not task_id:
        raise HTTPException(
            status_code=502,
            detail=data or "Meshy did not return a task id.",
        )

    return {"task_id": task_id}


@router.post("/generate")
async def generate_3d(req: GenerateRequest):
    job_id = req.job_id
    job_folder = UPLOAD_DIR / job_id

    if not job_folder.exists():
        return {"error": "Upload folder not found"}

    images = list(job_folder.glob("*"))

    if not images:
        return {"error": "No images found"}

    image_path = images[0]

    with open(image_path, "rb") as file_handle:
        image_base64 = base64.b64encode(file_handle.read()).decode()

    data_uri = f"data:image/png;base64,{image_base64}"

    payload = {
        "image_url": data_uri,
        "enable_pbr": True,
        "should_texture": True,
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


@router.get("/job/{task_id}")
def check_status(task_id: str):
    try:
        response = requests.get(
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
        data = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Meshy returned a non-JSON response during status polling.",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=data)

    status = (data.get("status") or "").strip().upper() or "PENDING"
    progress = _extract_progress_value(data.get("progress", 0))

    if status == "SUCCEEDED":
        model_urls = data.get("model_urls") or {}
        glb_url = (model_urls.get("glb") or "").strip()
        save_model(glb_url, task_id)
        return {
            "status": "SUCCEEDED",
            "progress": 100,
            "model_url": f"/outputs/{task_id}/model.glb?ts={task_id}",
        }

    if status in TERMINAL_FAILURE_STATUSES:
        return {
            "status": status,
            "progress": progress,
            "error": _extract_failure_message(data),
        }

    return {
        "status": status,
        "progress": progress,
    }


@router.post("/generate-free")
async def generate_free(req: GenerateRequest):
    job_id = req.job_id
    job_folder = UPLOAD_DIR / job_id

    if not job_folder.exists():
        return {"error": "No upload"}

    return {
        "status": "DONE",
        "model_url": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
    }
