from PIL import Image
from io import BytesIO
import base64

def image_to_base64(img_path: str) -> str:
    img = Image.open(img_path).convert("RGB")
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()
