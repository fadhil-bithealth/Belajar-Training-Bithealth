from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from app.services.pipeline import run_pipeline
from app.schemas.response_schema import FinalOutput

router = APIRouter()

@router.post("/detect", response_model=FinalOutput)
async def detect_image(images: List[UploadFile] = File(...)):
    if not images:
        raise HTTPException(
            status_code=400,
            detail="No image files uploaded. Please upload at least one image."
        )

    pil_images = []
    try:
        for image_file in images:
            contents = await image_file.read()
            image = Image.open(BytesIO(contents))
            pil_images.append(image)
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="One or more uploaded files are not valid image files or Not supported formats."
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="An error occurred while processing the images."
        )

    result = run_pipeline(pil_images)
    return result
