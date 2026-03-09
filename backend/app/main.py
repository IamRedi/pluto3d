from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.upload import router as upload_router
from app.routes.generate import router as generate_router
from app.routes.svg import router as svg_router

app = FastAPI(
    title="Pluto3D API",
    description="Photo to 3D and SVG generator",
    version="1.0"
)

# ==============================
# CORS (FIX për frontend)
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# ROUTES
# ==============================

app.include_router(upload_router, prefix="/api")
app.include_router(generate_router, prefix="/api")
app.include_router(svg_router, prefix="/api")

# ==============================
# STATIC FILES
# ==============================

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# ==============================
# ROOT
# ==============================

@app.get("/")
def root():
    return {
        "app": "Pluto3D Studio",
        "status": "running",
        "version": "1.0"
    }