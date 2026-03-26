import asyncio
from pathlib import Path
import os
import tempfile

from fastapi import APIRouter, File, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.services.mesh_repair import load_and_repair_mesh


router = APIRouter()
PRINT_FIX_QUEUE = asyncio.Semaphore(1)
UPLOAD_CHUNK_SIZE = 1024 * 1024


@router.post("/api/print-fix")
async def print_fix(file: UploadFile = File(...)):
    input_path = None

    try:
        async with PRINT_FIX_QUEUE:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".glb") as tmp:
                input_path = tmp.name

                while True:
                    chunk = await file.read(UPLOAD_CHUNK_SIZE)
                    if not chunk:
                        break
                    tmp.write(chunk)

            mesh = await run_in_threadpool(load_and_repair_mesh, input_path, None)

            filename = os.path.basename(input_path).replace(".glb", "_fixed.stl")

            base_dir = Path(__file__).resolve().parent.parent.parent
            outputs_dir = base_dir / "outputs" / "print"
            outputs_dir.mkdir(parents=True, exist_ok=True)

            output_path = outputs_dir / filename
            await run_in_threadpool(mesh.export, str(output_path))

            return {
                "status": "success",
                "file": f"/outputs/print/{filename}"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        try:
            await file.close()
        except Exception:
            pass

        if input_path and os.path.exists(input_path):
            try:
                os.remove(input_path)
            except OSError:
                pass
