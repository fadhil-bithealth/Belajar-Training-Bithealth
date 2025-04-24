from typing import List
from PIL import Image
import base64
import io

from app.utils.graph import build_graph
from app.schemas.response_schema import FinalOutput

# Build the LangGraph once
graph = build_graph()

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

    # Jalankan graph LangGraph
    result = graph.invoke({"images": image_inputs})

    # Ambil hasil final_output
    return result["final_output"]
