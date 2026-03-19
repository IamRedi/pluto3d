from fastapi import APIRouter
from pydantic import BaseModel
import trimesh
import numpy as np
import os
import uuid

router = APIRouter()

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "toy"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ToyRequest(BaseModel):
    prompt: str
    template: str
    size: int


def create_robot(size):
    # trup
    body = trimesh.creation.box(extents=(size, size*0.6, size*0.3))

    # koke
    head = trimesh.creation.box(extents=(size*0.6, size*0.6, size*0.6))
    head.apply_translation([0, 0, size*0.5])

    return trimesh.util.concatenate([body, head])


def create_car(size):
    base = trimesh.creation.box(extents=(size, size*0.5, size*0.2))

    wheel1 = trimesh.creation.cylinder(radius=size*0.2, height=0.2)
    wheel1.apply_translation([size*0.4, 0, -size*0.2])

    wheel2 = wheel1.copy()
    wheel2.apply_translation([-size*0.8, 0, 0])

    return trimesh.util.concatenate([base, wheel1, wheel2])


def create_figure(size):
    return trimesh.creation.icosphere(radius=size*0.5)


@router.post("/generate-toy")
def generate_toy(req: ToyRequest):

    try:
       size = float(req.size) / 5
    except:
       size = 1.0  # normalize

    if req.template == "robot":
        mesh = create_robot(size)

    elif req.template == "car":
        mesh = create_car(size)

    elif req.template == "figure":
        mesh = create_figure(size)

    else:
        # AUTO → zgjedh sipas prompt
        if "car" in req.prompt.lower():
            mesh = create_car(size)
        elif "robot" in req.prompt.lower():
            mesh = create_robot(size)
        else:
            mesh = create_figure(size)

    # -------- STL (për download) --------
    filename_stl = f"{uuid.uuid4()}.stl"
    path_stl = OUTPUT_DIR / filename_stl
    mesh.export(str(path_stl))

    # -------- GLB (për viewer) --------
    filename_glb = f"{uuid.uuid4()}.glb"
    path_glb = OUTPUT_DIR / filename_glb
    mesh.export(str(path_glb))

    return {
    "stl_url": f"/outputs/toy/{filename_stl}",
    "glb_url": f"/outputs/toy/{filename_glb}"
    }