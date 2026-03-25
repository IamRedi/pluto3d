import requests
from app.config import get_meshy_api_key

def generate_3d_from_image(image_path):
    meshy_api_key = get_meshy_api_key()

    if not meshy_api_key:
        raise RuntimeError(
            "Meshy 3D generation is not configured on this backend. "
            "Set MESHY_API_KEY and restart the server."
        )

    url = "https://api.meshy.ai/openapi/v1/image-to-3d"

    headers = {
        "Authorization": f"Bearer {meshy_api_key}"
    }

    files = {
        "image": open(image_path, "rb")
    }

    response = requests.post(url, headers=headers, files=files)

    return response.json()
