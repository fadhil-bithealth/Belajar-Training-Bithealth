
from fastapi import APIRouter, UploadFile, File
from typing import List
from PIL import Image
from io import BytesIO
from app.services.pipeline import run_pipeline
from app.schemas.response_schema import FinalOutput

router = APIRouter()

@router.post("/detect", response_model=FinalOutput)
async def detect_image(images: List[UploadFile] = File(...)):
    pil_images = []

    for image_file in images:
        contents = await image_file.read()
        image = Image.open(BytesIO(contents))
        pil_images.append(image)

    result = run_pipeline(pil_images)
    return result
