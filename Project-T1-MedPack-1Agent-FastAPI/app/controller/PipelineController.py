# app/controller/PipelineController.py

from typing import List
from PIL import Image
import base64
import io

from app.controller.AgentController import agentController  # <-- ini fix

from app.schemas.response_schema import FinalOutput

class PipelineController:
    def __init__(self):
        pass  

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

        # Jalankan anomaly check
        anomaly_result = agentController.run_anomaly_check(image_inputs)

        if anomaly_result.is_anomaly:
            # Kalau ada anomaly, langsung format output
            return agentController.run_output_formatting(anomaly_result)

        # Kalau tidak ada anomaly, lanjut image detection
        detection_result = agentController.run_image_detection(image_inputs)
        return agentController.run_output_formatting(anomaly_result, detection_result)

# Buat instance global
pipelineController = PipelineController()
