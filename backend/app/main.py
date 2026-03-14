from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routes.upload import router as upload_router
from app.routes.generate import router as generate_router
from app.routes.svg import router as svg_router


app = FastAPI(
    title="Pluto3D API",
    description="Photo to 3D and SVG generator",
    version="1.0"
)

# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS

app.include_router(upload_router, prefix="/api")
app.include_router(generate_router, prefix="/api")
app.include_router(svg_router, prefix="/api")

# PATH FIX (Railway safe)

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUTS_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "static"

OUTPUTS_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

# STATIC FILES

app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ROOT

@app.get("/")
def root():
    return {
        "app": "Pluto3D Studio",
        "status": "running"
    }