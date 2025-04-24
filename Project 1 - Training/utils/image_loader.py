import base64
from fastapi import UploadFile

async def prepare_images(uploaded_images: list[UploadFile]) -> list[str]:
    base64_images = []
    for image in uploaded_images:
        contents = await image.read()
        encoded = base64.b64encode(contents).decode("utf-8")
        mime_type = image.content_type  # biasanya 'image/jpeg' atau 'image/png'
        data_url = f"data:{mime_type};base64,{encoded}"
        base64_images.append(data_url)
    return base64_images
