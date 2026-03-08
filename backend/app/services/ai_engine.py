import requests
from app.config import MESHY_API_KEY

def generate_3d_from_image(image_path):

    url = "https://api.meshy.ai/openapi/v1/image-to-3d"

    headers = {
        "Authorization": f"Bearer {MESHY_API_KEY}"
    }

    files = {
        "image": open(image_path, "rb")
    }

    response = requests.post(url, headers=headers, files=files)

    return response.json()