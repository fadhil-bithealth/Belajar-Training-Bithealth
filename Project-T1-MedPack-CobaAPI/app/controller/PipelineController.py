from typing import List
from PIL import Image
import base64
import io

from app.controller.GraphController import graphController  # <-- Import instance, bukan build_graph
from app.schemas.response_schema import FinalOutput

class PipelineController:
    def __init__(self):
        # Pakai instance graphController langsung
        self.graph = graphController

    def run_pipeline(self, pil_images: List[Image.Image]) -> FinalOutput:
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

        # Jalankan LangGraph dengan input gambar
        result = self.graph.invoke({"images": image_inputs})

        # Ambil hasil final_output dari output graph
        return result["final_output"]

# Buat instance global
pipelineController = PipelineController()
