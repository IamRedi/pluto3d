from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
TOY_ASSET_VERSION = "2026-03-27-toy-map-2"


class ToyRequest(BaseModel):
    prompt: str
    template: str | None = None
    size: int | None = 1


@router.post("/generate-toy")
async def generate_toy(req: ToyRequest):
    try:
        query = req.prompt.lower()
        local_pluto_robot = f"/frontend/models/pluto-robot.glb?v={TOY_ASSET_VERSION}"
        local_f1_car = f"/frontend/models/f1car.glb?v={TOY_ASSET_VERSION}"

        # SIMPLE SMART MATCH
        if "dog" in query:
            model_url = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"

        elif "f1" in query or "car" in query:
            model_url = local_f1_car

        elif "robot" in query:
            model_url = local_pluto_robot

        else:
            model_url = local_pluto_robot

        return {
            "stl_url": None,
            "glb_url": model_url
        }

    except Exception as e:
        return {
            "error": str(e)
        }
