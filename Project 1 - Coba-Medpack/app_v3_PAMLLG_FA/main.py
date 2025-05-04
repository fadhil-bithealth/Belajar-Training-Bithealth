from fastapi import FastAPI, UploadFile, File
from app_v3_PAMLLG_FA.AppController import process_images
from typing import List
import shutil
from pathlib import Path
from app_v3_PAMLLG_FA.HttpResponseUtils import response_success, response_error

app = FastAPI()

@app.get("/")
def home():
    return {
        'message' : 'server is running'
    }

# @app.post("/detect/")
# async def detect(images: List[UploadFile] = File(...)):
#     save_dir = Path("assets")
#     image_paths = []
#     for image in images:
#         save_path = save_dir / image.filename
#         with open(save_path, "wb") as buffer:
#             shutil.copyfileobj(image.file, buffer)
#         image_paths.append(str(save_path))

#     result = process_images(image_paths)

#     return response_success(result)


@app.post("/detect/")
async def detect(images: List[UploadFile] = File(...)):
    save_dir = Path("assets")
    save_dir.mkdir(parents=True, exist_ok=True)  # pastikan folder ada

    image_paths = []

    try:
        for image in images:
            save_path = save_dir / image.filename

            # Validasi ekstensi file gambar
            if not image.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                return response_error(
                    f"[WARN] Format tidak didukung: {image.filename}",
                    msg="Hanya file gambar (.jpg, .jpeg, .png) yang didukung.",
                    code=422
                )

            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            image_paths.append(str(save_path))

        # Jalankan pipeline deteksi
        result = process_images(image_paths)
        return response_success(result)

    except Exception as e:
        return response_error(str(e))
