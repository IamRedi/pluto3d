import os
from fastapi import APIRouter, Form, UploadFile, File
import replicate

router = APIRouter()

client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

@router.post("/api/ai-photo")
async def ai_photo(
    prompt: str = Form(""),
    style: str = Form(""),
    image: UploadFile = File(None)
):

    try:

        if not prompt:
            prompt = "high quality product photo"

        final_prompt = prompt

        if style:
            final_prompt = f"{prompt}, {style} style"

        output = client.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": final_prompt + ", ultra detailed, studio lighting, 4k"
            }
        )

        # Flux kthen iterator → marrim elementin e parë
        image_url = None

        for item in output:
            image_url = str(item)
            break

        return {"image_url": image_url}

    except Exception as e:

        print("AI ERROR:", e)

        return {"error": str(e)}