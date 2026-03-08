from pathlib import Path
MESHY_API_KEY = "msy_T9jWxETIneGlPEgz5hIXR4QGAxXjPR2Sg2fU"
BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
