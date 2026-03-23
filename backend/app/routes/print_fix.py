from fastapi import APIRouter, UploadFile, File
import trimesh
import tempfile
import os
from pathlib import Path

router = APIRouter()

@router.post("/api/print-fix")
async def print_fix(file: UploadFile = File(...)):
    try:
        # 🔹 save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".glb") as tmp:
            tmp.write(await file.read())
            input_path = tmp.name

        # 🔹 load mesh
        mesh = trimesh.load(input_path, force='mesh')

        # 🔥 nëse është Scene → bashkoje në një mesh
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

        # =========================
        # 🔧 PRINT FIX PIPELINE
        # =========================

        # 🔹 FIX 1: mbush vrimat
        mesh.fill_holes()

        # 🔹 FIX 2: pastro mesh
        mesh.remove_degenerate_faces()
        mesh.remove_unreferenced_vertices()

        # 🔹 FIX 3: clean topology
        mesh.remove_duplicate_faces()
        mesh.merge_vertices()

        # 🔹 FIX 4 (opsional): ul poligonet (perfekt për print)
        try:
            mesh = mesh.simplify_quadratic_decimation(50000)
        except:
            pass  # nëse dështon, vazhdo normal

        # =========================
        # 💾 EXPORT
        # =========================

        filename = os.path.basename(input_path).replace(".glb", "_fixed.stl")

        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        OUTPUTS_DIR = BASE_DIR / "outputs" / "print"

        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

        output_path = OUTPUTS_DIR / filename

        mesh.export(str(output_path))

        # =========================
        # 📤 RESPONSE
        # =========================

        return {
            "status": "success",
            "file": f"/outputs/print/{filename}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }