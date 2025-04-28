from app.primary_agent import run_agent
from app.schema import FinalOutput
from PIL import Image
from typing import List
import base64
import io

def run_pipeline(pil_images: List[Image.Image]) -> FinalOutput:
    image_inputs = []
    for img in pil_images:
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        base64_img = base64.b64encode(buf.getvalue()).decode()
        image_inputs.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_img}"
            }
        })

    result = run_agent(image_inputs)
    return result
