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

        # Flux ndonjëherë kthen generator
        image_url = None

        if isinstance(output, list):
            image_url = output[0]

        else:
            image_url = str(output)

        return {
            "image_url": image_url
        }

    except Exception as e:

        return {
            "error": str(e)
        }