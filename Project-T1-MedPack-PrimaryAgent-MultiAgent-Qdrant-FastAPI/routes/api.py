from fastapi import APIRouter, Header, Depends
from typing import Annotated
import app.schemas as schemas
from app.utils.HttpResponseUtils import response_error, response_success
from app.controller.AppController import appController
# Load environment variables
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from app.controller.PipelineController import run_pipeline
from app.schemas.schemas import FinalOutput
from PIL import Image
import io
import os
from langchain.callbacks import tracing_v2_enabled
from dotenv import load_dotenv
load_dotenv()
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")


router = APIRouter()

@router.get("/")
def get_action():
    return appController.get_app_info()

@router.post("/process-images/", response_model=FinalOutput)
async def process_images(images: List[UploadFile] = File(...)):
    if not images or len(images) == 0:
        return response_error(
            error="[WARN] No images uploaded",
            msg="No images uploaded. Please upload at least one image.",
            code=400
        )
    try:
        pil_images = []
        for image in images:
            content = await image.read()
            pil_image = Image.open(io.BytesIO(content)).convert("RGB")
            pil_images.append(pil_image)
        
        with tracing_v2_enabled(project_name=LANGSMITH_PROJECT):
            result = run_pipeline(pil_images)
        
        return result
    except Exception as e:
        return response_error(
            error=str(e),
            msg="Internal server error while processing images",
            code=500
        )
