import base64
import requests
import os
from uuid import uuid4

url = "https://api.minimaxi.com/v1/image_generation"
api_key = os.environ.get("MINIMAX_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}

payload = {
    "model": "image-01",
    "prompt": "Describe the image in detail",  # Example: Men Dressing in white t shirt, full-body stand front view image :25, outdoor, Venice beach sign, full-body image, Los Angeles, Fashion photography of 90s, documentary, Film grain, photorealistic.
    "aspect_ratio": "{aspect_ratio}",  # Examples: 16:9, 9:16, 4:3, 3:4, 1:1
    "response_format": "base64",
}

response = requests.post(url, headers=headers, json=payload)
response.raise_for_status()

images = response.json()["data"]["image_base64"]

image_names = []
for i in range(len(images)):
    image_name = f"image-{uuid4()}.jpeg"
    with open(image_name, "wb") as f:
        f.write(base64.b64decode(images[i]))
        image_names.append(image_name)

print(image_names)
