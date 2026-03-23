from pathlib import Path
import os
import tempfile

from fastapi import APIRouter, File, UploadFile

from app.services.mesh_repair import load_and_repair_mesh


router = APIRouter()


@router.post("/api/print-fix")
async def print_fix(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".glb") as tmp:
            tmp.write(await file.read())
            input_path = tmp.name

        mesh = load_and_repair_mesh(input_path)

        filename = os.path.basename(input_path).replace(".glb", "_fixed.stl")

        base_dir = Path(__file__).resolve().parent.parent.parent
        outputs_dir = base_dir / "outputs" / "print"
        outputs_dir.mkdir(parents=True, exist_ok=True)

        output_path = outputs_dir / filename
        mesh.export(str(output_path))

        return {
            "status": "success",
            "file": f"/outputs/print/{filename}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
