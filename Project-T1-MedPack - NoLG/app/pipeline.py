# app/pipeline.py

from app.agent import run_anomaly_check, run_image_detection, run_output_formatting
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

    anomaly_result = run_anomaly_check(image_inputs)

    if anomaly_result.is_anomaly:
        return run_output_formatting(anomaly_result)

    detection_result = run_image_detection(image_inputs)
    return run_output_formatting(anomaly_result, detection_result)
