from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ToyRequest(BaseModel):
    prompt: str
    template: str | None = None
    size: int | None = 1


@router.post("/api/generate-toy")
async def generate_toy(req: ToyRequest):
    try:
        query = req.prompt.lower()

        # SIMPLE SMART MATCH
        if "dog" in query:
            model_url = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"

        elif "car" in query:
            model_url = "https://modelviewer.dev/shared-assets/models/Car.glb"

        elif "robot" in query:
            model_url = "https://modelviewer.dev/shared-assets/models/RobotExpressive.glb"

        else:
            model_url = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"

        return {
            "stl_url": None,
            "glb_url": model_url
        }

    except Exception as e:
        return {
            "error": str(e)
        }