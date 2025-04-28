# app/controller/PipelineController.py

from typing import List
from PIL import Image
import base64
import io
import asyncio
from app.graph.GraphBuilder import pipeline_graph, PipelineState
from app.schemas.response_schema import FinalOutput


class PipelineController:
    def __init__(self):
        pass

    async def run_pipeline(self, pil_images: List[Image.Image]) -> FinalOutput:
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
        input_state = PipelineState(images=image_inputs)

        # Run LangGraph pipeline
        result = await pipeline_graph.ainvoke({"images": image_inputs})
        return result['final_output']


pipelineController = PipelineController()
