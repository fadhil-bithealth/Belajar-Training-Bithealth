from fastapi import FastAPI, UploadFile, File
from app_v3_PAMLLG_FA.AppController import process_images
from typing import List
import shutil
from pathlib import Path

app = FastAPI()

@app.get("/")
def home():
    return {
        'message' : 'server is running'
    }

@app.post("/detect/")
async def detect(images: List[UploadFile] = File(...)):
    save_dir = Path("assets")
    image_paths = []
    for image in images:
        save_path = save_dir / image.filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_paths.append(str(save_path))

    result = process_images(image_paths)
    return result
