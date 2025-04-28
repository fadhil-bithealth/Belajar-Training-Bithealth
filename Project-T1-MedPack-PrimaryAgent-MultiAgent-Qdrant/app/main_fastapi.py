# main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from app.pipeline import run_pipeline
from app.schema import FinalOutput
from PIL import Image
import io
import os
from dotenv import load_dotenv
from langchain.callbacks import tracing_v2_enabled

# Load environment variables
load_dotenv()
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Server is running!"}

@app.post("/process-images/", response_model=FinalOutput)
async def process_images(images: List[UploadFile] = File(...)):
    if not images or len(images) == 0:
        raise HTTPException(
            status_code=400,
            detail="No images uploaded. Please upload at least one image."
        )
    
    try:
        pil_images = []
        for image in images:
            content = await image.read()
            pil_image = Image.open(io.BytesIO(content)).convert("RGB")
            pil_images.append(pil_image)
        
        # Tambahkan tracing di sini
        with tracing_v2_enabled(project_name=LANGSMITH_PROJECT):
            result = run_pipeline(pil_images)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR NO IMAGES UPLOADED or Internal server error: {str(e)}")
